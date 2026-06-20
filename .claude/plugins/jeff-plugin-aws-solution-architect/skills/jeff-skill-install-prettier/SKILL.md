---
name: jeff-skill-install-prettier
description: Install prettier. Use when setting up a dev environment, fixing TypeScript and JavaScript formatting issues, or asked to "install prettier", "configure prettier", or "set up code formatting".
---

Before proceeding, ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.

1. Create `.prettierrc.json` in the project root if it doesn't already exist.
2. The content of `.prettierrc.json` should at a minimum contain every setting listed below (do not remove any existing setting just ensure these settings all exist and if not add them):
   ```json
   {
     "printWidth": 120,
     "singleQuote": true,
     "semi": true,
     "tabWidth": 2,
     "trailingComma": "none",
     "endOfLine": "lf"
   }
   ```
3. Create `.prettierignore` in the project root if it doesn't already exist.
4. The content of `.prettierignore` should at a minimum contain every setting listed below (do not remove any existing setting just ensure these settings all exist and if not add them):
   ```
   node_modules
   dist
   build
   coverage
   ```
5. If a `package.json` file exists in the project root, ensure `prettier:fix` and `prettier:check` are listed as `scripts` command, and if these commands don't exist add them.
   ```json
    "scripts":{
      "prettier:fix": "npx prettier --write .",
      "prettier:check": "npx prettier --check ."
    }
   ```
6. If a `package.json` file does NOT exist in the project root, create or append to a `Makefile` with prettier commands:
   - If `Makefile` already exists, append the prettier targets to it (only if they don't already exist)
   - If `Makefile` doesn't exist, create it with the prettier targets

   ```makefile
   .PHONY: prettier-fix prettier-check

   prettier-fix:
   	npx prettier --write .

   prettier-check:
   	npx prettier --check .
   ```

7. There is no reason to have prettier configuration or dependency (outside of the two `prettier:fix` and `prettier:check` script commands in package.json, or the prettier targets in Makefile) in `package.json` or any other file. If extra prettier configuration exists in `package.json` or any other file, remove it to avoid confusion and ensure all configuration is in `.prettierrc.json` and `.prettierignore`. This also applies to "nested" `package.json` files in subdirectories (for example projects that have a `client` or `cdk` directory).

## Additional resources

- Refer to the Prettier documentation if you need help: https://prettier.io/docs/
