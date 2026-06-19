#!/usr/bin/env python3
"""Vulcan remote-compute helper for the ITB engine.

Thin Paramiko wrapper to run commands / push files to the Vulcan server
(192.168.4.178) so heavy numerical experiments run off the laptop.

Usage:
    python tools/vulcan.py run "uname -a"
    python tools/vulcan.py put local.py /remote/path.py
    python tools/vulcan.py get /remote/out.json local.json

Authentication:
    Defaults to key auth using ~/.ssh/id_ed25519. Override with VULCAN_KEY.
    Set VULCAN_PASS only for one-time bootstrap or emergency password auth.
"""
import os
import shlex
import sys
from pathlib import Path

import paramiko

# Credentials come from the environment so no secret is committed.
HOST = os.environ.get("VULCAN_HOST", "192.168.4.178")
USER = os.environ.get("VULCAN_USER", "admin")
PASS = os.environ.get("VULCAN_PASS")
KEY = os.environ.get("VULCAN_KEY", str(Path.home() / ".ssh" / "id_ed25519"))


def _client():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs = {
        "hostname": HOST,
        "username": USER,
        "timeout": 15,
    }
    if PASS:
        kwargs.update(password=PASS, look_for_keys=False, allow_agent=False)
    else:
        kwargs.update(
            key_filename=KEY if Path(KEY).exists() else None,
            look_for_keys=True,
            allow_agent=True,
        )
    c.connect(**kwargs)
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
    stage = "/tmp/_vulcan_stage_" + os.path.basename(remote)
    c = _client()
    try:
        sftp = c.open_sftp()
        sftp.put(local, stage)
        sftp.close()
        remote_q = shlex.quote(remote)
        stage_q = shlex.quote(stage)
        cmd = f"mkdir -p $(dirname {remote_q}) && mv -f {stage_q} {remote_q}"
        stdin, stdout, stderr = c.exec_command(cmd)
        code = stdout.channel.recv_exit_status()
        if code:
            err = stderr.read().decode("utf-8", "replace")
            raise RuntimeError(f"remote put failed ({code}): {err}")
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
