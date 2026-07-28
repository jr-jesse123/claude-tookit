#!/usr/bin/env node
/**
 * Validates the marketplace catalog and every plugin it lists.
 *
 * No dependencies — runs on any Node 18+. Exits 1 when there is at least one
 * error; warnings alone still exit 0.
 *
 * Usage: node scripts/validate-marketplace.mjs [repo-root]
 */

import { readFileSync, readdirSync, statSync, accessSync, constants } from "node:fs";
import { join, relative, resolve, sep } from "node:path";

const ROOT = resolve(process.argv[2] ?? join(import.meta.dirname, ".."));
const MARKETPLACE = join(ROOT, ".claude-plugin", "marketplace.json");

const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;

// Names Anthropic reserves for official marketplaces.
const RESERVED = new Set([
  "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
  "claude-plugins-community", "claude-community", "anthropic-marketplace",
  "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
  "knowledge-work-plugins", "life-sciences", "claude-for-legal",
  "claude-for-financial-services", "financial-services-plugins",
  "first-party-plugins", "healthcare",
]);

// plugin.json fields that hold paths into the plugin directory.
const PATH_FIELDS = [
  "skills", "commands", "agents", "workflows", "hooks", "mcpServers",
  "outputStyles", "lspServers",
];

const errors = [];
const warnings = [];

const rel = (p) => relative(ROOT, p) || ".";
const err = (where, msg) => errors.push(`${where}: ${msg}`);
const warn = (where, msg) => warnings.push(`${where}: ${msg}`);

function exists(p) {
  try {
    statSync(p);
    return true;
  } catch {
    return false;
  }
}

function isDir(p) {
  try {
    return statSync(p).isDirectory();
  } catch {
    return false;
  }
}

function readJson(path) {
  let raw;
  try {
    raw = readFileSync(path, "utf8");
  } catch {
    err(rel(path), "file not found");
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (e) {
    err(rel(path), `invalid JSON — ${e.message}`);
    return null;
  }
}

/** Minimal top-level YAML frontmatter reader. Returns null when absent. */
function frontmatter(path) {
  const raw = readFileSync(path, "utf8");
  if (!raw.startsWith("---")) return null;
  const end = raw.indexOf("\n---", 3);
  if (end === -1) return null;
  const block = raw.slice(raw.indexOf("\n") + 1, end);
  const fields = {};
  for (const line of block.split("\n")) {
    if (!line.trim() || line.startsWith("#") || /^\s/.test(line)) continue;
    const idx = line.indexOf(":");
    if (idx === -1) continue;
    fields[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
  }
  return fields;
}

function listFiles(dir, ext) {
  if (!isDir(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(ext))
    .map((f) => join(dir, f));
}

/** Plugins may not reference anything outside their own directory. */
function assertInside(where, pluginDir, value) {
  if (typeof value !== "string") return;
  if (value.split(/[\\/]/).includes("..")) {
    err(where, `path "${value}" escapes the plugin directory — "../" is not allowed`);
    return;
  }
  const target = resolve(pluginDir, value.replace("${CLAUDE_PLUGIN_ROOT}", "."));
  if (target !== pluginDir && !target.startsWith(pluginDir + sep)) {
    err(where, `path "${value}" resolves outside the plugin directory`);
  }
}

function validateSkills(pluginDir, name) {
  const skillsDir = join(pluginDir, "skills");
  if (!isDir(skillsDir)) return;
  for (const entry of readdirSync(skillsDir)) {
    const dir = join(skillsDir, entry);
    if (!isDir(dir)) continue;
    const skillFile = join(dir, "SKILL.md");
    const where = `${name} → ${rel(skillFile)}`;
    if (!exists(skillFile)) {
      err(`${name} → ${rel(dir)}`, "skill directory has no SKILL.md");
      continue;
    }
    const fm = frontmatter(skillFile);
    if (!fm) {
      warn(where, "no YAML frontmatter — description falls back to the first paragraph");
      continue;
    }
    if (!fm.description) warn(where, "frontmatter has no `description`; Claude uses it to decide when to load the skill");
    if (fm.name && !KEBAB.test(fm.name)) err(where, `frontmatter name "${fm.name}" is not kebab-case`);
    if (fm.name && fm.name !== entry) {
      warn(where, `frontmatter name "${fm.name}" differs from directory name "${entry}"`);
    }
  }
}

function validateAgents(pluginDir, name) {
  for (const file of listFiles(join(pluginDir, "agents"), ".md")) {
    const where = `${name} → ${rel(file)}`;
    const fm = frontmatter(file);
    if (!fm) {
      err(where, "agent file has no YAML frontmatter");
      continue;
    }
    if (!fm.name) err(where, "agent frontmatter is missing `name`");
    else if (!KEBAB.test(fm.name)) err(where, `agent name "${fm.name}" is not kebab-case`);
    if (!fm.description) err(where, "agent frontmatter is missing `description`");
    for (const forbidden of ["hooks", "mcpServers", "permissionMode"]) {
      if (forbidden in fm) err(where, `\`${forbidden}\` is not supported in plugin-shipped agents`);
    }
  }
}

function validateCommands(pluginDir, name) {
  for (const file of listFiles(join(pluginDir, "commands"), ".md")) {
    const where = `${name} → ${rel(file)}`;
    const fm = frontmatter(file);
    if (fm && !fm.description) warn(where, "command has frontmatter but no `description`");
  }
}

function validateHooks(pluginDir, name) {
  const hooksFile = join(pluginDir, "hooks", "hooks.json");
  if (!exists(hooksFile)) return;
  const config = readJson(hooksFile);
  if (!config) return;
  const where = `${name} → ${rel(hooksFile)}`;
  if (!config.hooks || typeof config.hooks !== "object") {
    err(where, "missing top-level `hooks` object");
    return;
  }
  for (const [event, matchers] of Object.entries(config.hooks)) {
    if (!Array.isArray(matchers)) {
      err(where, `hooks.${event} must be an array`);
      continue;
    }
    for (const matcher of matchers) {
      for (const hook of matcher.hooks ?? []) {
        if (hook.type !== "command" || typeof hook.command !== "string") continue;
        const script = hook.command.replace(/"/g, "").split(/\s+/)[0];
        if (!script.includes("${CLAUDE_PLUGIN_ROOT}")) {
          warn(where, `command "${script}" does not use \${CLAUDE_PLUGIN_ROOT}; plugins run from a cache directory, not from the repo`);
          continue;
        }
        assertInside(where, pluginDir, script);
        const target = resolve(pluginDir, script.replace("${CLAUDE_PLUGIN_ROOT}/", ""));
        if (!exists(target)) {
          err(where, `hook script not found: ${rel(target)}`);
          continue;
        }
        try {
          accessSync(target, constants.X_OK);
        } catch {
          err(where, `hook script is not executable: ${rel(target)} (run \`git update-index --chmod=+x\`)`);
        }
      }
    }
  }
}

function validateMcp(pluginDir, name) {
  const mcpFile = join(pluginDir, ".mcp.json");
  if (!exists(mcpFile)) return;
  const config = readJson(mcpFile);
  if (!config) return;
  const where = `${name} → ${rel(mcpFile)}`;
  if (!config.mcpServers || typeof config.mcpServers !== "object") {
    err(where, "missing top-level `mcpServers` object");
    return;
  }
  for (const [server, cfg] of Object.entries(config.mcpServers)) {
    for (const value of [cfg.command, ...(cfg.args ?? [])]) {
      if (typeof value === "string" && value.includes("${CLAUDE_PLUGIN_ROOT}")) {
        assertInside(`${where} → ${server}`, pluginDir, value);
      }
    }
  }
}

function validatePlugin(entry, index) {
  const label = entry?.name ?? `plugins[${index}]`;

  if (typeof entry?.name !== "string") {
    err(label, "missing required field `name`");
  } else if (!KEBAB.test(entry.name)) {
    err(label, `name "${entry.name}" is not kebab-case`);
  }

  if (entry?.source === undefined) {
    err(label, "missing required field `source`");
    return;
  }
  if (typeof entry.source !== "string") return; // remote source: nothing local to check

  if (entry.source.split("/").includes("..")) {
    err(label, `source "${entry.source}" uses "../", which is not allowed`);
    return;
  }

  const pluginDir = resolve(ROOT, entry.source);
  if (!isDir(pluginDir)) {
    err(label, `source directory not found: ${entry.source}`);
    return;
  }

  const manifestPath = join(pluginDir, ".claude-plugin", "plugin.json");
  if (exists(manifestPath)) {
    const manifest = readJson(manifestPath);
    if (manifest) {
      const where = `${label} → ${rel(manifestPath)}`;
      if (typeof manifest.name !== "string") err(where, "missing required field `name`");
      else if (!KEBAB.test(manifest.name)) err(where, `name "${manifest.name}" is not kebab-case`);
      else if (manifest.name !== entry.name) {
        warn(where, `name "${manifest.name}" differs from the marketplace entry "${entry.name}"; the marketplace name is what users install`);
      }
      if (manifest.keywords !== undefined && !Array.isArray(manifest.keywords)) {
        err(where, "`keywords` must be an array");
      }
      if (manifest.version !== undefined && entry.version !== undefined) {
        warn(where, "`version` is set in both plugin.json and the marketplace entry; plugin.json always wins");
      }
      for (const field of PATH_FIELDS) {
        const value = manifest[field];
        for (const item of Array.isArray(value) ? value : [value]) {
          if (typeof item === "string") assertInside(where, pluginDir, item);
        }
      }
    }
  } else {
    warn(label, "no .claude-plugin/plugin.json — components are auto-discovered and the name comes from the directory");
  }

  const hasComponents = ["skills", "commands", "agents", "hooks"].some((d) => isDir(join(pluginDir, d))) ||
    exists(join(pluginDir, "SKILL.md")) || exists(join(pluginDir, ".mcp.json"));
  if (!hasComponents) warn(label, "plugin ships no skills, commands, agents, hooks, or MCP servers");

  validateSkills(pluginDir, label);
  validateAgents(pluginDir, label);
  validateCommands(pluginDir, label);
  validateHooks(pluginDir, label);
  validateMcp(pluginDir, label);
}

function main() {
  const marketplace = readJson(MARKETPLACE);

  if (marketplace) {
    const where = rel(MARKETPLACE);
    if (typeof marketplace.name !== "string") err(where, "missing required field `name`");
    else if (!KEBAB.test(marketplace.name)) err(where, `name "${marketplace.name}" is not kebab-case`);
    else if (RESERVED.has(marketplace.name)) err(where, `name "${marketplace.name}" is reserved for official Anthropic marketplaces`);

    if (!marketplace.owner?.name) err(where, "missing required field `owner.name`");

    if (!Array.isArray(marketplace.plugins)) {
      err(where, "missing required field `plugins` (array)");
    } else {
      if (marketplace.plugins.length === 0) warn(where, "the catalog lists no plugins");
      const seen = new Set();
      marketplace.plugins.forEach((entry, i) => {
        if (entry?.name) {
          if (seen.has(entry.name)) err(where, `duplicate plugin name "${entry.name}"`);
          seen.add(entry.name);
        }
        validatePlugin(entry, i);
      });
    }
  }

  // Catch plugin directories that exist on disk but are not in the catalog.
  const pluginsDir = join(ROOT, "plugins");
  if (isDir(pluginsDir) && Array.isArray(marketplace?.plugins)) {
    const listed = new Set(
      marketplace.plugins
        .filter((p) => typeof p?.source === "string")
        .map((p) => resolve(ROOT, p.source))
    );
    for (const entry of readdirSync(pluginsDir)) {
      const dir = join(pluginsDir, entry);
      if (isDir(dir) && !listed.has(dir)) {
        warn(rel(dir), "directory is not listed in marketplace.json, so nobody can install it");
      }
    }
  }

  for (const w of warnings) console.log(`  warning  ${w}`);
  for (const e of errors) console.log(`  error    ${e}`);

  if (errors.length) {
    console.log(`\n✗ ${errors.length} error(s), ${warnings.length} warning(s)`);
    process.exit(1);
  }
  console.log(`\n✓ marketplace is valid (${warnings.length} warning(s))`);
}

main();
