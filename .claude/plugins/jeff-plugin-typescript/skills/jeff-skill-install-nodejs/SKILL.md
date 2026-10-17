---
name: jeff-skill-install-nodejs
description: Install the latest LTS (Long Term Support) version of Node.js using nvm (Node Version Manager). Use when setting up a dev environment, fixing Node.js version issues, or asked to "install node", "update node", or "set up nvm".
---

`nvm` is a shell function, not a binary, so non-interactive shells (including Claude Code's Bash tool) must load it first. Prefix every `nvm` command in this skill with:

```bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
```

1. Run `nvm --version`. If nvm is missing, install it with the official script, using the latest release tag from https://github.com/nvm-sh/nvm/releases:

   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/<latest-tag>/install.sh | bash
   ```

   Don't install nvm through Homebrew or apt; nvm doesn't support those installs.

2. Compare `nvm version-remote --lts` with `nvm current`.
3. If they differ:
   - `nvm install --lts`
   - `nvm alias default 'lts/*'` so new shells use it
   - Confirm `node --version` matches the LTS version from step 2.
4. If the repo has an `.nvmrc`, run `nvm use` in the repo and make sure `.nvmrc` holds the current LTS major.
