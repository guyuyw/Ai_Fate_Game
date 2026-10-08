"""Validate *design examples* against v1 contract; not a runtime engine."""
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'examples' / 'DEMO_midnight_hospital'
SCHEMAS = ROOT / 'schemas'

def load(p: Path): return json.loads(p.read_text(encoding='utf8'))

manifest = load(BASE / 'manifest.json')
manifest_schema = load(SCHEMAS / 'manifest.schema.json')
task_schema = load(SCHEMAS / 'task.schema.json')
Draft7Validator.check_schema(manifest_schema)
Draft7Validator.check_schema(task_schema)
Draft7Validator(manifest_schema).validate(manifest)
print('PASS 1: manifest JSON Schema')

for p in manifest['references'].values():
    assert '/' not in p and (BASE / p).is_file(), f'missing reference file {p}'
print('PASS 2: all manifest file references resolve')

world=load(BASE / manifest['references']['world'])
characters=load(BASE / manifest['references']['characters'])
roles=load(BASE / manifest['references']['playerRoles'])
scenes=load(BASE / manifest['references']['scenes'])
tasks=load(BASE / manifest['references']['tasks'])['tasks']
fate=load(BASE / manifest['references']['fate'])
opening=load(BASE / manifest['references']['opening'])
for t in tasks: Draft7Validator(task_schema).validate(t)
for label in ('world','characters','player_roles','scenes','fate','opening'):
    schema = load(SCHEMAS / f'{label}.schema.json')
    Draft7Validator.check_schema(schema)
    Draft7Validator(schema).validate(load(BASE / f'{label}.json'))
print('PASS 3: all 8 schema categories including 3 tasks')

char_ids={c['id'] for c in characters['characters']}
scene_ids={s['id'] for s in scenes['scenes']}
role_ids={r['id'] for r in roles['roles']}
fact_ids={f['id'] for f in world['facts']}
task_ids={t['id'] for t in tasks}
baseline_event_ids={b['referenceEventId'] for b in fate['baselineFates']}

for label, data in [('characters',char_ids),('scenes',scene_ids),('roles',role_ids),('facts',fact_ids),('tasks',task_ids),('events',baseline_event_ids)]:
    count={'characters':len(characters['characters']),'scenes':len(scenes['scenes']),
           'roles':len(roles['roles']),'facts':len(world['facts']),'tasks':len(tasks),
           'events':len(fate['baselineFates'])}[label]
    assert len(data)==count, f'duplicate {label}'
entry=manifest['entry']
assert entry['sceneId'] in scene_ids
assert entry['protagonistId'] in char_ids
assert entry['defaultRoleId'] in role_ids
assert opening['startingSceneId'] in scene_ids
for msg in opening['messages']: assert msg['senderId'] in char_ids
for f in world['facts']: assert set(f.get('initialKnownTo',[])) <= char_ids
for ch in characters['characters']:
    assert ch['initialState']['locationId'] in scene_ids
    assert set(ch['initialState']['knownFactIds']) <= fact_ids
for r in characters['relations']:
    assert r['subjectId'] in char_ids and r['targetId'] in char_ids
for r in roles['roles']: assert set(r['initialKnownFactIds']) <= fact_ids
print('PASS 4: unique IDs and actor/scene/role/fact cross references')


def check_condition(rule):
    op=rule['op']
    if op in ('all','any'):
        for x in rule['rules']:check_condition(x)
    if op=='not':check_condition(rule['rule'])
    if op in ('actor_alive','fact_known'):assert rule['actorId'] in char_ids
    if op=='fact_known':assert rule['factId'] in fact_ids
    if op=='task_state':assert rule['taskId'] in task_ids
    if op=='event_occurred':assert rule['eventId'] in baseline_event_ids
    if op=='relation_gte':assert rule['subjectId'] in char_ids and rule['targetId'] in char_ids

def check_effect(x):
    if x['type'] in ('grant_fact','actor_alive'):assert x['actorId'] in char_ids
    if x['type']=='grant_fact':assert x['factId'] in fact_ids
    if x['type']=='task_transition':assert x['taskId'] in task_ids
    if x['type']=='unlock_scene':assert x['sceneId'] in scene_ids
    if x['type'] in ('revoke_event','schedule_event'):assert x['eventId'] in baseline_event_ids
    if x['type']=='relation_delta':assert x['subjectId'] in char_ids and x['targetId'] in char_ids

for t in tasks:
    assert t['ownerId'] in char_ids
    for field in ('prerequisites','succeedsWhen','failsWhen'):check_condition(t[field])
    for effect in t['onSuccess']+t['onFailure']:check_effect(effect)
for b in fate['baselineFates']:
    check_condition(b['trigger'])
    check_condition(b['cancelIf'])
    for effect in b['effects']:check_effect(effect)
print('PASS 5: task, fate condition and effect cross references')

# Simple schema negative checks: invalid op must fail, root required missing must fail.
invalid=tasks[0].copy()
invalid['succeedsWhen']={'op':'execute_js','code':'malicious()'}
assert not Draft7Validator(task_schema).is_valid(invalid)
invalid_manifest=manifest.copy(); invalid_manifest.pop('packId')
assert not Draft7Validator(manifest_schema).is_valid(invalid_manifest)
print('PASS 6: expected invalid manifest/task rejected')
print('DESIGN FIXTURE VALIDATION: 6/6 PASS — No browser/runtime functionality tested')
