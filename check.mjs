#!/usr/bin/env node
/**
 * Skill-library validator. Zero dependencies, Node 18+.
 *
 *   node check.mjs        exit 0 = library is consistent; exit 1 = contract broken
 *
 * Enforces the contract in CLAUDE.md:
 *  - INDEX.md and skills/*.md are a bijection (every file indexed once, every row real)
 *  - ranks are sequential 1..N
 *  - every skill has the standard anatomy (Why this exists / Rules or The patterns);
 *    a missing Worked example is a warning, since README permits stating the absence
 *  - skills stay under a page (~800 words) — outgrown means "split it"
 *  - INDEX read-cost estimates track actual file length (warn at >30% drift)
 *  - counts stated in README.md ("N skill files", "all N skills") match reality
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const SKILLS = path.join(ROOT, 'skills');
const WORD_CAP = 800;
const TOKENS_PER_WORD = 1.3;
const DRIFT_TOLERANCE = 0.30;

const errors = [];
const warnings = [];

const files = fs.readdirSync(SKILLS)
  .filter((f) => f.endsWith('.md') && f !== 'INDEX.md')
  .sort();
const index = fs.readFileSync(path.join(SKILLS, 'INDEX.md'), 'utf8');
const readme = fs.readFileSync(path.join(ROOT, 'README.md'), 'utf8');

/* ── INDEX ↔ files bijection ── */
const rows = [...index.matchAll(/^\|\s*(\d+)\s*\|\s*\[`([^`]+)`\]\(([^)]+)\)\s*\|/gm)]
  .map((m) => {
    const cells = m.input.slice(m.index).split('\n')[0].split('|');
    return { rank: Number(m[1]), name: m[2], link: m[3], readCostCell: cells[4] || '' };
  });

const indexed = new Map();
for (const r of rows) {
  if (r.name !== r.link) errors.push(`INDEX rank ${r.rank}: link target (${r.link}) differs from displayed name (${r.name})`);
  if (indexed.has(r.name)) errors.push(`INDEX lists ${r.name} more than once (ranks ${indexed.get(r.name).rank} and ${r.rank})`);
  indexed.set(r.name, r);
  if (!files.includes(r.name)) errors.push(`INDEX rank ${r.rank} points to skills/${r.name}, which does not exist`);
}
for (const f of files) {
  if (!indexed.has(f)) errors.push(`skills/${f} exists but is missing from INDEX.md — every skill must be indexed and ranked`);
}
rows.forEach((r, i) => {
  if (r.rank !== i + 1) errors.push(`INDEX ranks are not sequential: expected ${i + 1}, found ${r.rank} (${r.name}) — renumber after adding/removing`);
});

/* ── per-file anatomy + length ── */
for (const f of files) {
  const body = fs.readFileSync(path.join(SKILLS, f), 'utf8');
  const words = body.split(/\s+/).filter(Boolean).length;

  if (!/^## Why this exists/m.test(body)) errors.push(`skills/${f}: missing "## Why this exists" — every skill must state the failure mode it prevents`);
  if (!/^## (Rules|The patterns)/m.test(body)) errors.push(`skills/${f}: missing "## Rules" (or "## The patterns") — skills must be followable, not just described`);
  if (!/^## Worked example/m.test(body)) warnings.push(`skills/${f}: no "## Worked example" section — allowed only if the file explains why (never invent an anecdote to fill it)`);
  if (words > WORD_CAP) warnings.push(`skills/${f}: ${words} words (> ${WORD_CAP}) — "if a skill outgrows a page, it's two skills"`);

  /* read-cost drift vs INDEX */
  const row = indexed.get(f);
  if (row) {
    const est = row.readCostCell.match(/~?([\d,]+)/);
    if (!est) { warnings.push(`INDEX row for ${f}: no read-cost estimate found in the "Read cost" column`); continue; }
    const claimed = Number(est[1].replace(/,/g, ''));
    const actual = Math.round(words * TOKENS_PER_WORD);
    const drift = Math.abs(claimed - actual) / actual;
    if (drift > DRIFT_TOLERANCE) {
      warnings.push(`INDEX read cost for ${f} is ~${claimed} tokens but the file measures ~${actual} (${Math.round(drift * 100)}% off) — update the estimate (words × 1.3)`);
    }
  }
}

/* ── counts stated in prose ── */
for (const m of readme.matchAll(/\b(\d+)\s+skill files?\b/g)) {
  if (Number(m[1]) !== files.length) errors.push(`README.md says "${m[0]}" but skills/ contains ${files.length} skill files — update the count`);
}
for (const m of readme.matchAll(/\ball (\d+)\s+skills?\b/g)) {
  if (Number(m[1]) !== files.length) errors.push(`README.md says "${m[0]}" but skills/ contains ${files.length} skill files — update the count`);
}

/* ── report ── */
for (const e of errors) console.log(`✗ ${e}`);
for (const w of warnings) console.log(`△ ${w}`);
console.log(errors.length || warnings.length
  ? `${errors.length} error(s), ${warnings.length} warning(s) across ${files.length} skills.`
  : `✓ library consistent — ${files.length} skills, all indexed, anatomy intact, estimates in tolerance`);
process.exit(errors.length ? 1 : 0);
