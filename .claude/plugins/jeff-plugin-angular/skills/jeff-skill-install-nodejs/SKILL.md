---
name: jeff-skill-install-nodejs
description: Install the latest LTS (Long Term Support) version of Node.js using nvm (Node Version Manager). Use when setting up a dev environment, fixing Node.js version issues, or asked to "install node", "update node", or "set up nvm".
---

1. Check if `nvm` is already installed by running `nvm --version`.
   - If not installed, install it using the host's package manager (Homebrew for macOS, apt for Ubuntu, etc...).
   - After installing, ensure `nvm` is loaded in the current shell (restart the shell if not detected after install).
2. Check the latest LTS version available:
   - Run `nvm version-remote --lts` and note the version.
3. Check the currently active Node.js version:
   - Run `nvm current`.
4. If the versions do not match:
   - Run `nvm install --lts` to install.
   - Run `nvm alias default lts/*` to set it as the default for new shells.
   - Run `node --version` to verify it matches the LTS version from step 2.

## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
