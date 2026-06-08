#!/usr/bin/env python3
"""Vulcan remote-compute helper for the ITB engine.

Thin paramiko wrapper to run commands / push files to the Vulcan server
(192.168.4.178) so heavy numerical experiments run off the laptop.

Usage:
    python tools/vulcan.py run "uname -a"
    python tools/vulcan.py put local.py /remote/path.py
    python tools/vulcan.py get /remote/out.json local.json
"""
import os
import sys
import paramiko

# Credentials come from the environment so no secret is committed.
#   PowerShell:  $env:VULCAN_PASS="..."   (and optionally VULCAN_HOST/VULCAN_USER)
HOST = os.environ.get("VULCAN_HOST", "192.168.4.178")
USER = os.environ.get("VULCAN_USER", "admin")
PASS = os.environ.get("VULCAN_PASS")
if not PASS:
    sys.exit("set VULCAN_PASS (and optionally VULCAN_HOST/VULCAN_USER) in the environment")


def _client():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=15,
              look_for_keys=False, allow_agent=False)
    return c


def run(cmd, timeout=600):
    c = _client()
    try:
        stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return code, out, err
    finally:
        c.close()


def put(local, remote):
    # Some SFTP servers ENOENT on direct open-for-write in subdirs; stage in
    # /tmp then mv into place via exec.
    import os
    stage = "/tmp/_vulcan_stage_" + os.path.basename(remote)
    c = _client()
    try:
        sftp = c.open_sftp()
        sftp.put(local, stage)
        sftp.close()
        _, out, err = c.exec_command(f"mkdir -p $(dirname '{remote}') && mv -f '{stage}' '{remote}'")[0:3]
        out.channel.recv_exit_status()
    finally:
        c.close()


def get(remote, local):
    c = _client()
    try:
        sftp = c.open_sftp()
        sftp.get(remote, local)
        sftp.close()
    finally:
        c.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    op = sys.argv[1]
    if op == "run":
        code, out, err = run(sys.argv[2])
        sys.stdout.write(out)
        if err:
            sys.stderr.write(err)
        sys.exit(code)
    elif op == "put":
        put(sys.argv[2], sys.argv[3])
        print(f"put {sys.argv[2]} -> {sys.argv[3]}")
    elif op == "get":
        get(sys.argv[2], sys.argv[3])
        print(f"get {sys.argv[2]} -> {sys.argv[3]}")
    else:
        print(f"unknown op: {op}")
        sys.exit(1)
