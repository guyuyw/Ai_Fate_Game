/**
 * Dependency-free integrity and structural preflight for the Codex handoff.
 * IMPORTANT: This validates handoff assets, NOT a running P1 game engine.
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
let checks = 0;
const fail = (msg) => { errors.push(msg); };
const ok = (pass, message) => {
  checks += 1;
  if (pass) console.log(`PASS ${checks}: ${message}`);
  else { console.log(`FAIL ${checks}: ${message}`); fail(message); }
};
const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const json = (relative) => JSON.parse(readFileSync(join(root, relative), 'utf8'));
const unique = (arr) => Array.isArray(arr) && new Set(arr).size === arr.length;

let manifest;
try {
  manifest = json('HANDOFF_MANIFEST.json');
  let filesExist = true;
  let validDigests = true;
  for (const file of manifest.immutableFiles) {
    if (!file.path || file.path.startsWith('/') || file.path.includes('..') || file.path.includes('\\')) {
      filesExist = false; continue;
    }
    const filename = join(root, file.path);
    if (!existsSync(filename) || !statSync(filename).isFile()) { filesExist = false; continue; }
    const bytes = readFileSync(filename);
    if (bytes.length !== file.bytes || sha256(bytes) !== file.sha256) validDigests = false;
  }
  ok(filesExist, `immutable files present (${manifest.immutableFiles.length})`);
  ok(filesExist && validDigests, 'immutable file SHA-256 and byte lengths match the manifest');
} catch (e) {
  ok(false, `handoff manifest failed: ${e.message}`);
}

let demo = {};
let source = {};
const names = ['manifest', 'world', 'characters', 'player_roles', 'scenes', 'tasks', 'fate', 'opening'];
try {
  let allPresent = true;
  let same = true;
  for (const name of names) {
    const a = `reference/demo_storypack/${name}.json`;
    const b = `reference/architecture/examples/DEMO_midnight_hospital/${name}.json`;
    if (!existsSync(join(root, a)) || !existsSync(join(root, b))) { allPresent = false; continue; }
    demo[name] = json(a);
    source[name] = json(b);
    if (sha256(readFileSync(join(root, a))) !== sha256(readFileSync(join(root, b)))) same = false;
  }
  ok(allPresent && Object.keys(demo).length === 8, 'all 8 demo JSON documents are present and parseable');
  ok(allPresent && same, 'demo JSON documents exactly match architecture reference examples');
} catch (e) {
  ok(false, `demo JSON parse failed: ${e.message}`);
}

try {
  const base = 'reference/architecture/schemas/';
  const schemas = ['manifest', 'world', 'characters', 'player_roles', 'scenes', 'task', 'fate', 'opening'];
  ok(schemas.every((s) => json(`${base}${s}.schema.json`).$schema?.includes('draft-07')), '8 design schema files exist, parse and declare JSON Schema draft-07');
} catch (e) {
  ok(false, `schema file parse failed: ${e.message}`);
}

try {
  const m = demo.manifest;
  const dir = join(root, 'reference/demo_storypack');
  const referenced = Object.values(m.references ?? {});
  ok(m.format === 'aifate.storypack' && referenced.length === 7 && referenced.every((f) => typeof f === 'string' && /^[A-Za-z_]+\.json$/.test(f) && existsSync(join(dir, f))), 'demo manifest references 7 valid files');
  const actors = demo.characters.characters.map((x) => x.id);
  const facts = demo.world.facts.map((x) => x.id);
  const scenes = demo.scenes.scenes.map((x) => x.id);
  const roles = demo.player_roles.roles.map((x) => x.id);
  const tasks = demo.tasks.tasks.map((x) => x.id);
  ok([actors, facts, scenes, roles, tasks].every(unique), 'demo actor/fact/scene/role/task IDs are unique');
  ok(actors.includes(m.entry.protagonistId) && scenes.includes(m.entry.sceneId) && roles.includes(m.entry.defaultRoleId), 'entry actor, scene, role references resolve');
  ok(demo.characters.characters.every((x) => scenes.includes(x.initialState.locationId) && x.initialState.knownFactIds.every((f) => facts.includes(f))), 'actor initial fact and scene references resolve');
} catch (e) {
  ok(false, `cross-reference preflight failed: ${e.message}`);
}

try {
  const fixture = json('fixtures/p1_scenarios.json');
  const ids = fixture.cases.map((c) => c.id);
  ok(fixture.fixtureKind === 'authoritative-test-events-only' && fixture.storyPackId === demo.manifest.packId && fixture.cases.length >= 5 && unique(ids), 'P1 test specification cases are present and have unique IDs');
  ok(fixture.cases.every((c) => c.startMinute <= c.advanceToMinute && c.actions.every((a) => a.atMinute >= c.startMinute && a.atMinute <= c.advanceToMinute && ['test_fixture', 'late_player_request', 'untrusted_model'].includes(a.source))), 'scenario timing and source declarations are coherent');
} catch (e) {
  ok(false, `fixture parse or structure failed: ${e.message}`);
}

ok(existsSync(join(root, 'AGENTS.md')) && existsSync(join(root, 'CODEX_START_HERE.md')), 'Codex instructions present');
ok(existsSync(join(root, 'reference/architecture/contracts/runtime.ts')), 'TypeScript contract present');

if (errors.length) {
  console.error(`\nHANDOFF PREFLIGHT: ${checks - errors.length}/${checks} PASS; NOT READY`);
  process.exitCode = 1;
} else {
  console.log(`\nHANDOFF PREFLIGHT: ${checks}/${checks} PASS`);
  console.log('NOTE: Handoff integrity and structural checks ONLY; no P1 runtime behavior was tested.');
}
