#!/usr/bin/env python3
"""Consult Dr. M. — the local Gemma-4 research partner on Pluto.

Posts a physics prompt to the OpenAI-compatible endpoint at 192.168.4.193:8080
and prints the reply. Used as a co-theorist / adversarial critic for the ITB
realism program.
"""
import json
import sys
import urllib.request

URL = "http://192.168.4.193:8080/v1/chat/completions"
MODEL = "gemma-4-26b-a4b-it"


def ask(system, user, max_tokens=2000, temperature=0.6):
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }).encode()
    req = urllib.request.Request(URL, data=body,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        data = json.load(r)
    msg = data["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    fin = data["choices"][0].get("finish_reason")
    if content.strip():
        return content
    # reasoning model that spent its budget thinking — surface the reasoning
    return f"[finish_reason={fin}; content empty, showing reasoning]\n\n{reasoning}"


if __name__ == "__main__":
    sysmsg = open(sys.argv[1]).read() if len(sys.argv) > 1 else "You are a helpful physicist."
    usermsg = open(sys.argv[2]).read() if len(sys.argv) > 2 else sys.stdin.read()
    mt = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    print(ask(sysmsg, usermsg, max_tokens=mt))
