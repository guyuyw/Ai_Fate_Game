import json
from pathlib import Path
base=Path(__file__).resolve().parents[1] / 'examples' / 'DEMO_midnight_hospital'
base.mkdir(parents=True,exist_ok=True)

def write(name,x):
 (base/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

write('manifest.json',{
 'format':'aifate.storypack','schemaVersion':'1.0.0','packId':'demo.midnight_hospital','version':'0.1.0',
 'title':'午夜病院：远程协助（虚构 DEMO）','language':'zh-CN',
 'description':'演示人物知识隔离、远程协助、任务裁定以及原著命运可能改写。非成品游戏。',
 'licensing':{'rightsholder':'DEMO / 原创虚构占位','usage':'original-demo','distribution':'demo-only'},
 'entry':{'sceneId':'scene.hall','protagonistId':'char.lin','defaultRoleId':'role.expert'},
 'time':{'mode':'on_resume','startStoryMinute':0,'maxCatchupHours':12,'timeScale':1},
 'references':{'world':'world.json','characters':'characters.json','playerRoles':'player_roles.json',
               'scenes':'scenes.json','tasks':'tasks.json','fate':'fate.json','opening':'opening.json'},
 'assets':[]
})
write('world.json',{
 'worldRules':[
  {'id':'rule.fixed_time','immutable':True,'description':'叙事时间单向推进，人物不能穿越已确定的过去。'},
  {'id':'rule.evidence','immutable':True,'description':'主角不能凭空获得证据；只有实际检查和他人合法披露可以增加所知事实。'}
 ],
 'facts':[
  {'id':'fact.exit_route','description':'西走廊紧急出口可通往屋顶楼梯。','initialKnownTo':[],'hiddenFromPlayerAtStart':True},
  {'id':'fact.lab_location','description':'被封锁的研究室在三层东端。','initialKnownTo':['char.chen'],'hiddenFromPlayerAtStart':True},
  {'id':'fact.witness_in_lab','description':'失踪的目击者可能被锁在研究室。','initialKnownTo':['char.chen'],'hiddenFromPlayerAtStart':True},
  {'id':'fact.source_of_fog','description':'雾来自二十年前研究设施的事故。','initialKnownTo':['char.chen'],'hiddenFromPlayerAtStart':True}
 ],
 'flags':{'witness_rescued':False,'lab_door_open':False,'main_power_on':True,'mission_failed':False}
})
write('characters.json',{
 'characters':[
  {'id':'char.lin','name':'林默','kind':'protagonist','persona':'沉着但会冒险救人；尊重证据，不机械服从玩家。',
   'goals':['找到失踪目击者','安全离开医院'],
   'initialState':{'alive':True,'locationId':'scene.hall','health':100,'stress':30,'knownFactIds':[], 'inventoryItemIds':['item.flashlight']}},
  {'id':'char.chen','name':'陈博士','kind':'npc','persona':'熟悉研究所但刻意隐瞒事故核心事实；不轻易交出资料。',
   'goals':['不暴露事故真相','确保研究室封闭'],
   'initialState':{'alive':True,'locationId':'scene.laboratory','health':100,'stress':40,'knownFactIds':['fact.lab_location','fact.witness_in_lab','fact.source_of_fog'],'inventoryItemIds':[]}},
  {'id':'char.ye','name':'叶宁','kind':'npc','persona':'失踪目击者，渴望获救，但会因恐惧拒绝陌生人的命令。',
   'goals':['活着离开医院'],
   'initialState':{'alive':True,'locationId':'scene.laboratory','health':60,'stress':75,'knownFactIds':[],'inventoryItemIds':[]}}
 ],
 'relations':[
  {'subjectId':'char.lin','targetId':'char.chen','trust':10,'respect':20,'affinity':0,'caution':80},
  {'subjectId':'char.ye','targetId':'char.lin','trust':0,'respect':0,'affinity':0,'caution':50}
 ]
})
write('player_roles.json',{
 'roles':[
  {'id':'role.bystander','title':'远程路人','permissions':['send_advice','request_media'],
   'initialKnownFactIds':[],'initialTrustBias':0,'description':'可以建议，但没有特殊权能。'},
  {'id':'role.expert','title':'远程调查专家','permissions':['send_advice','request_media','annotate_evidence'],
   'initialKnownFactIds':[],'initialTrustBias':10,'description':'可提供专业分析，无法凭空生成证据。'},
  {'id':'role.system','title':'异常通讯系统','permissions':['send_advice','request_media','issue_system_hint'],
   'initialKnownFactIds':[],'initialTrustBias':5,'description':'系统提示仅限剧情预授权范围；不能修改世界事实。'}
 ]
})
write('scenes.json',{
 'scenes':[
  {'id':'scene.hall','title':'医院二层走廊','access':'initial','availableObjects':['item.flashlight','obj.exit_sign']},
  {'id':'scene.laboratory','title':'三层研究室','access':'locked','availableObjects':['obj.lab_door']},
  {'id':'scene.roof','title':'屋顶楼梯','access':'locked','availableObjects':[]}
 ]
})
EMPTY={'op':'all','rules':[]}
FALSE={'op':'flag_eq','flag':'mission_failed','value':True}
write('tasks.json',{
 'tasks':[
  {'id':'task.find_route','ownerId':'char.lin','title':'确认可撤离路线','initialState':'active',
   'prerequisites':EMPTY,
   'succeedsWhen':{'op':'fact_known','actorId':'char.lin','factId':'fact.exit_route'},
   'failsWhen':FALSE,
   'onSuccess':[{'type':'unlock_scene','sceneId':'scene.roof'}], 'onFailure':[]},
  {'id':'task.interview','ownerId':'char.lin','title':'取得研究室位置线索','initialState':'locked',
   'prerequisites':{'op':'task_state','taskId':'task.find_route','value':'succeeded'},
   'succeedsWhen':{'op':'fact_known','actorId':'char.lin','factId':'fact.lab_location'},
   'failsWhen':FALSE,
   'onSuccess':[{'type':'unlock_scene','sceneId':'scene.laboratory'}], 'onFailure':[]},
  {'id':'task.save_witness','ownerId':'char.lin','title':'拯救被困目击者','initialState':'locked',
   'prerequisites':{'op':'task_state','taskId':'task.interview','value':'succeeded'},
   'succeedsWhen':{'op':'flag_eq','flag':'witness_rescued','value':True},
   'failsWhen':{'op':'event_occurred','eventId':'event.witness_death'},
   'onSuccess':[{'type':'revoke_event','eventId':'event.witness_death'},
                {'type':'relation_delta','subjectId':'char.ye','targetId':'char.lin','dimension':'trust','delta':20}],
   'onFailure':[{'type':'set_flag','flag':'mission_failed','value':True}],
   'deadlineMinute':120}
 ]
})
write('fate.json',{
 'baselineFates':[
  {'id':'fate.witness_death','referenceEventId':'event.witness_death',
   'description':'原著基准：主角未及时救援，目击者在两小时后死亡。',
   'trigger':{'op':'all','rules':[{'op':'story_time_gte','minute':120},
                                 {'op':'flag_eq','flag':'witness_rescued','value':False},
                                 {'op':'actor_alive','actorId':'char.ye','value':True}]},
   'cancelIf':{'op':'flag_eq','flag':'witness_rescued','value':True},
   'effects':[{'type':'actor_alive','actorId':'char.ye','alive':False}]
  }
 ]
})
write('opening.json',{
 'startingSceneId':'scene.hall',
 'messages':[{'id':'msg.opening.01','senderId':'char.lin','type':'text',
              'content':'我已经进入二楼走廊，前面分成两条路。你能帮我判断下一步吗？','storyMinute':0}]
})
print('created files:',*[p.name for p in base.glob('*.json')])
