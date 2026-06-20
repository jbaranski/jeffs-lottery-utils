#!/usr/bin/env node
// Recomputes the SHA-256 hash of the first inline <script> in src/index.html
// and writes the updated hash into the script-src directive in netlify.toml.
// Run this after changing the PostHog snippet, then commit both files.
const { createHash } = require('node:crypto');
const { readFileSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');

const root = join(__dirname, '..');

const indexHtml = readFileSync(join(root, 'src/index.html'), 'utf8');
const match = indexHtml.match(/<script>([\s\S]*?)<\/script>/);
if (!match) {
  console.error('No inline <script> found in src/index.html');
  process.exit(1);
}

const hash = `sha256-${createHash('sha256').update(match[1], 'utf8').digest('base64')}`;

const tomlPath = join(root, 'netlify.toml');
const toml = readFileSync(tomlPath, 'utf8');
const updated = toml.replace(/'sha256-[A-Za-z0-9+/=]+'/, `'${hash}'`);

if (updated === toml) {
  console.log(`CSP hash already up to date: '${hash}'`);
} else {
  writeFileSync(tomlPath, updated);
  console.log(`netlify.toml updated with: '${hash}'`);
}
