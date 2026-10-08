"""Build remaining v1 JSON Schema files for typed storypack payloads."""
from __future__ import annotations
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
schema_dir=root/'schemas'
task=json.loads((schema_dir/'task.schema.json').read_text(encoding='utf8'))
ID=task['definitions']['id']
def arr(items,minItems=0):return {'type':'array','items':items,'minItems':minItems}
def obj(required, props, extra=False):return {'type':'object','additionalProperties':extra,'required':required,'properties':props}
def s(min_len=0,max_len=10000):return {'type':'string','minLength':min_len,'maxLength':max_len}
def refid():return {'$ref':'#/definitions/id'}
def wrapper(title, props, req, defs=None):
 d={'$schema':'http://json-schema.org/draft-07/schema#','title':title, **obj(req,props)}
 d['definitions']={'id':ID,**(defs or {})}
 return d

def write(name,x):
 (schema_dir/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

world_rule=obj(['id','immutable','description'],{'id':refid(),'immutable':{'type':'boolean'},'description':s(1,2000)})
fact=obj(['id','description','initialKnownTo','hiddenFromPlayerAtStart'],{'id':refid(),'description':s(1,2000),'initialKnownTo':arr(refid()),'hiddenFromPlayerAtStart':{'type':'boolean'}})
write('world.schema.json',wrapper('Story world',{
 'worldRules':arr(world_rule),'facts':arr(fact),
 'flags':{'type':'object','additionalProperties':{'type':['string','boolean','number']}}
},['worldRules','facts','flags']))

actor_state=obj(['alive','locationId','health','stress','knownFactIds','inventoryItemIds'],{
 'alive':{'type':'boolean'},'locationId':refid(),
 'health':{'type':'integer','minimum':0,'maximum':100},'stress':{'type':'integer','minimum':0,'maximum':100},
 'knownFactIds':arr(refid()),'inventoryItemIds':arr(refid())
})
character=obj(['id','name','kind','persona','goals','initialState'],{
 'id':refid(),'name':s(1,100),'kind':{'enum':['protagonist','npc']},'persona':s(1,5000),
 'goals':arr(s(1,250)), 'initialState':actor_state
})
relation=obj(['subjectId','targetId','trust','respect','affinity','caution'],{
 'subjectId':refid(),'targetId':refid(),**{k:{'type':'number','minimum':-100,'maximum':100} for k in ['trust','respect','affinity','caution']}
})
write('characters.schema.json',wrapper('Story characters',{'characters':arr(character,1),'relations':arr(relation)},['characters','relations']))

role=obj(['id','title','permissions','initialKnownFactIds','initialTrustBias','description'],{
 'id':refid(),'title':s(1,100),
 'permissions':{'type':'array','uniqueItems':True,'items':{'enum':['send_advice','request_media','annotate_evidence','issue_system_hint']}},
 'initialKnownFactIds':arr(refid()),'initialTrustBias':{'type':'number','minimum':-100,'maximum':100},
 'description':s(1,500)
})
write('player_roles.schema.json',wrapper('Story player roles',{'roles':arr(role,1)},['roles']))

scene=obj(['id','title','access','availableObjects'],{
 'id':refid(),'title':s(1,150),'access':{'enum':['initial','locked']},'availableObjects':arr(refid())
})
write('scenes.schema.json',wrapper('Story scenes',{'scenes':arr(scene,1)},['scenes']))

fate=obj(['id','referenceEventId','description','trigger','cancelIf','effects'],{
 'id':refid(),'referenceEventId':refid(),'description':s(1,2000),
 'trigger':{'$ref':'#/definitions/condition'}, 'cancelIf':{'$ref':'#/definitions/condition'},
 'effects':arr({'$ref':'#/definitions/effect'})
})
write('fate.schema.json',wrapper('Story baseline fates',{'baselineFates':arr(fate)},['baselineFates'],
                                {'condition':task['definitions']['condition'],'effect':task['definitions']['effect']}))
message=obj(['id','senderId','type','content','storyMinute'],{
 'id':refid(),'senderId':refid(),'type':{'const':'text'},'content':s(1,10000),
 'storyMinute':{'type':'integer','minimum':0}
})
write('opening.schema.json',wrapper('Story opening',{'startingSceneId':refid(),'messages':arr(message,1)},
                                    ['startingSceneId','messages']))
print('Generated 6 additional schemas')
