---
name: github-automation-fallbacks
description: "Use when gh CLI lacks scopes or auth fails on Windows."
version: 1.0.0
author: Lan Fang
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [github, git, credentials, auth, rest-api, ssh]
    category: software-development
    related_skills: [github]
---

# GitHub Automation Fallbacks

Guidance and recipes when standard `gh auth login` or interactive CLI flows fail on Windows / non-interactive agent environments.

## Common Obstacles & Solutions

### 1. `gh auth login --with-token` Fails Due to Missing Scopes
- **Problem**: Tokens extracted from Git Credential Manager often lack `read:org` scope required by the `gh` CLI (`error validating token: missing required scope 'read:org'`).
- **Solution**: Do not rely on `gh` in this case. Call GitHub REST API directly using Python or curl with `Authorization: Bearer <token>`.

### 2. Extracting Token from Existing Git Credentials
On Windows where Git Credential Manager or Windows Credential Manager holds credentials:
```bash
printf "protocol=https\nhost=github.com\n\n" | git credential fill
```
Extract `password=<token>` from the output.

### 3. Creating Repositories via REST API
When creating a repository programmatically without `gh`:
- Always use `Authorization: Bearer <token>` (avoid passing unquoted tokens through shells where special characters or carriage returns might truncate them).
- Pass proper JSON payload:
```python
import json
import urllib.request

req = urllib.request.Request(
    "https://api.github.com/user/repos",
    data=json.dumps({"name": repo_name, "private": False}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Agent",
    },
)
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    ssh_url = res["ssh_url"]
```

### 4. SSH Remote Push Fallback
If SSH key (`~/.ssh/id_ed25519` or `~/.ssh/id_rsa`) is already authenticated (`ssh -T git@github.com` says `Hi <username>!`), configure git remote to use SSH:
```bash
git remote add origin git@github.com:<username>/<repo>.git
git push -u origin <branch>
```
This bypasses HTTPS credential expiration and CLI permission constraints entirely.
