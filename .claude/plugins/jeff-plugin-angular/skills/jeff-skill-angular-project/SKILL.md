---
name: jeff-skill-angular-project
description: Install or update the Angular CLI to the latest version globally. Use when setting up a dev environment, ensuring Angular CLI is current, generating new projects, or when asked to "install Angular", "update Angular", "setup Angular", or "create a new Angular app".
---

## Prerequisites

Before proceeding:

1. Ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.
2. Use WebSearch to verify current versions:
   - "Angular latest version [current-year]"
   - "Tailwind CSS latest version [current-year]"
   - Visit https://nodejs.org/en to find the current Node.js LTS major version (look for the "LTS" badge)
   - Update any version references in examples below with verified versions
   - DO NOT skip this step. DO NOT guess at version numbers.

## Steps

1. Run `npm install -g @angular/cli` to install or update to the latest Angular CLI globally.
   - In the update scenario, run `ng update @angular/core @angular/cli` as well
2. Verify installation by running `ng version` and ensure the Angular CLI version is the latest available version.
3. Create a new project by running `ng new <project-name>` and follow the prompts to set up the project with the desired configuration.
   - Use `CSS` for stylesheet format
   - Do NOT enable server side rendering
4. Use the latest stable version of `tailwindcss` as a `devDependency`. Refer to the documentation at https://tailwindcss.com/docs.
   - To install run `ng add tailwindcss` and confirm any prompts. This is equivalent to doing the following (just here for your reference in case something goes wrong or needs to be fixed):
     - `npm install -D tailwindcss @tailwindcss/postcss postcss`
     - Configure `.postcssrc.json` with the following content:

     ```
     {
        "plugins": {
           "@tailwindcss/postcss": {}
        }
     }
     ```

     - `src/styles.css` should contain `@import "tailwindcss"`;

5. Set up Netlify deployment using the `jeff-skill-angular-netlify` skill.

6. Create `.nvmrc` in the project root with the current Node LTS major version (visit https://nodejs.org/en and look for the "LTS" badge):

   ```
   <NODE_LTS>
   ```

7. Add an `engines` field to `package.json` and create `.npmrc` to enforce the Node version:

   In `package.json`, add (replacing `<NODE_LTS>` with the current LTS major version):

   ```json
   "engines": {
     "node": ">= <NODE_LTS>.0.0"
   }
   ```

   Create `.npmrc` in the project root:

   ```
   engine-strict=true
   ```

   With `engine-strict=true`, any `npm` command on the wrong Node version will error immediately instead of silently corrupting the lock file.

8. Configure the session-start hook using the `session-start-hook` skill so that Claude Code web sessions automatically install the current Node LTS version at container startup.

## npm ci vs npm install

- **Use `npm ci`** in CI pipelines, fresh checkouts, and Claude Code web sessions. It installs exactly what is in `package-lock.json`, never modifies the lock file, and fails fast if the lock file is missing or inconsistent.
- **Use `npm install <package>`** only when intentionally adding or updating a dependency.
- **Never run bare `npm install`** (no arguments) in CI or fresh environments — it re-resolves versions and may silently rewrite the lock file, which defeats reproducibility and can break CI.

## Integration with Other Skills

- **jeff-skill-error-debugging-rca**: Use when debugging errors or test failures in Angular projects or related tools
- **jeff-skill-angular-aws-cognito**: Integrate AWS Cognito authentication into the Angular app
- **jeff-skill-angular-netlify**: Set up production Netlify deployment — full `netlify.toml` with caching headers, Makefile deploy target, and GitHub Actions CI/CD workflow
- **jeff-skill-tailwind-design-system**: Apply Tailwind v4 design tokens, component patterns, and theming after initial project setup

## Additional resources

- Refer to the Angular documentation if you need help: https://angular.io/docs
