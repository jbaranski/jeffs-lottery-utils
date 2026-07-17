---
name: jeff-skill-install-dependabot
description: Install and configure Dependabot for automated dependency updates in the project. Use when setting up a new dev environment, repository, adding dependency management, or asked to "install dependabot" or "set up automated updates".
---

1. Check if `.github/dependabot.yml` already exists in the project.
2. If `.github/dependabot.yml` does not already exist, create it.
   - For your reference, here is a minimal dependabot.yml file that monitors npm dependencies weekly, with updates grouped into a single PR:
   ```yaml
   version: 2
   updates:
   - package-ecosystem: "npm"
      directory: "/"
      schedule:
         interval: "weekly"
      groups:
         npm-dependencies:
            patterns:
               - "*"
   ```
3. Populate `.github/dependabot.yml` with the correct configuration for the project's dependencies. Here is a common use cases you will encounter (but this is listed just as an example, it is not exhaustive so refer to the "Additonal resources" if other dependencies are in scope):
   - Search the root of the project, and all subdirectories recursively, for `package.json` files. For each `package.json` file found, add an entry for `npm` dependencies in the `.github/dependabot.yml` file with the correct directory path to the `package.json` file. For example, if a `package.json` file is found in the root of the project, in a `client` directory, and in a `cdk` directory, the dependabot.yml file should have 3 entries for npm dependencies with the correct directory paths:

   ```yaml
   updates:
     - package-ecosystem: 'npm'
       directory: '/'
       schedule:
         interval: 'weekly'
       groups:
         npm-dependencies:
           patterns:
             - '*'
     - package-ecosystem: 'npm'
       directory: '/cdk'
       schedule:
         interval: 'weekly'
       groups:
         npm-dependencies:
           patterns:
             - '*'
     - package-ecosystem: 'npm'
       directory: '/client'
       schedule:
         interval: 'weekly'
       groups:
         npm-dependencies:
           patterns:
             - '*'
   ```

   - As of 02/08/2026, the full list of languages/technologies supported are: Bazel, Bundler, Bun, Cargo, Composer, Devcontainers, Docker, Docker Compose, Dotnet SDK, Elm, GitHub Actions, Gitsubmodule, Gomod (Go Modules), Gradle, Helm, Hex (Hex), Julia, Maven, NPM and Yarn, NuGet, OpenTofu, Pip, Pub, Swift, Terraform, UV. But you should always double check the "Additional resources" link below via WebSearch for the most up to date list of supported languages and technologies. Do not skip the WebSearch when confirming this.

4. **Every entry must include a `groups:` block.** Use `patterns: ['*']` to consolidate all of that entry's updates into a single PR (or a more deliberate split, e.g. by package prefix or major/minor/patch, if the project needs finer-grained review batches). An ungrouped entry lets Dependabot open one PR per outdated dependency — this is the single biggest driver of PR/issue floods and, on private repos, of wasted GitHub Actions minutes (each Dependabot update-check job itself runs on Actions-hosted runners). Never leave a `groups:` block out.

5. **Cap `interval` at `weekly`.** Do not configure `daily` for any entry, regardless of what a default example elsewhere suggests — daily simply multiplies the Actions-minute cost of Dependabot's own update checks for negligible benefit over weekly.

6. **Use `monthly` for low-churn directories** — one-off migration/backfill/seed scripts, archived or rarely-touched tooling, or any directory that isn't under active development. Reserve `weekly` for directories with actively-maintained, regularly-changing dependencies (main app/service code). When in doubt about a directory's churn, ask the user rather than defaulting to `weekly`.

7. Explain to the user why you chose the specific `directory` path, `groups` breakdown, and `interval` for each entry in the dependabot.yml file, and give links to specific documentation if available to further help them understand it's truly correct.

## Additional resources

- For the complete YAML spec, refer https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file
- For the official up to date list of supported languages and technologies, refer https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
- For grouped updates, refer https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference#groups
