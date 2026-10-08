/** Story Runtime Contracts v1.0 — Design-only, not an implementation. */
export type ID = string;
export type ISO8601 = string;

export type MessageProvenance =
  | 'authored_story' | 'in_world_capture' | 'player_external'
  | 'generated_illustration' | 'user_text' | 'model_text';

export type MessagePart =
  | { type: 'text'; text: string }
  | { type: 'image'; assetId: ID; provenance: MessageProvenance; caption?: string }
  | { type: 'audio'; assetId: ID; provenance: MessageProvenance; transcript?: string };

export interface ChatMessage {
  id: ID;
  runId: ID;
  senderId: ID;
  visibility: 'player' | 'narrator' | 'system_private';
  parts: MessagePart[];
  createdAt: ISO8601;
  storyMinute: number;
  basedOnEventIds: ID[];
  delivery: 'live' | 'catch_up';
}

export type Condition =
  | { op: 'all'; rules: Condition[] }
  | { op: 'any'; rules: Condition[] }
  | { op: 'not'; rule: Condition }
  | { op: 'flag_eq'; flag: string; value: string | number | boolean }
  | { op: 'fact_known'; actorId: ID; factId: ID }
  | { op: 'actor_alive'; actorId: ID; value: boolean }
  | { op: 'event_occurred'; eventId: ID }
  | { op: 'task_state'; taskId: ID; value: TaskState }
  | { op: 'relation_gte'; subjectId: ID; targetId: ID; dimension: string; value: number }
  | { op: 'story_time_gte'; minute: number };

export type Effect =
  | { type: 'set_flag'; flag: string; value: boolean | number | string }
  | { type: 'grant_fact'; actorId: ID; factId: ID }
  | { type: 'task_transition'; taskId: ID; state: TaskState }
  | { type: 'actor_alive'; actorId: ID; alive: boolean }
  | { type: 'relation_delta'; subjectId: ID; targetId: ID; dimension: string; delta: number }
  | { type: 'schedule_event'; eventId: ID; afterMinutes: number }
  | { type: 'revoke_event'; eventId: ID }
  | { type: 'unlock_scene'; sceneId: ID };

export type TaskState = 'locked' | 'available' | 'active' | 'succeeded' | 'failed' | 'cancelled';
export interface TaskSpec {
  id: ID;
  ownerId: ID;
  title: string;
  initialState: TaskState;
  prerequisites: Condition;
  succeedsWhen: Condition;
  failsWhen: Condition;
  onSuccess: Effect[];
  onFailure: Effect[];
  deadlineMinute?: number;
}

export interface ActorState {
  id: ID;
  alive: boolean;
  locationId: ID;
  health: number;
  stress: number;
  knownFactIds: ID[];
  inventoryItemIds: ID[];
  currentGoalIds: ID[];
  currentPlan?: { verb: string; targetId?: ID; estimatedMinutes?: number };
}
export interface Relation {
  subjectId: ID;
  targetId: ID;
  trust: number;
  respect: number;
  affinity: number;
  caution: number;
  /** Never assume a threshold forces romance, intimacy or consent. */
  boundaries: string[];
}
export interface GameState {
  runId: ID;
  packId: ID;
  packHash: string;
  revision: number;
  storyMinute: number;
  lastResumeUtc: ISO8601;
  randomSeed: string;
  actors: Record<ID, ActorState>;
  relations: Relation[];
  tasks: Record<ID, TaskState>;
  flags: Record<string, string | boolean | number>;
  occurredEventIds: ID[];
  pendingEventIds: ID[];
}

export interface ActionProposal {
  requestId: ID;
  actorId: ID;
  verb: 'move' | 'inspect' | 'ask' | 'share_information' | 'use_item' | 'wait' | 'decline' | 'request_help';
  targetId?: ID;
  parameters?: Record<string, string | number | boolean>;
  citedFactIds: ID[];
  motivation?: string; // not authoritative evidence
}
export type Verdict =
  | { accepted: true; producedEvents: GameEvent[]; explanationCode: string }
  | { accepted: false; producedEvents: []; explanationCode: string; recoverable: boolean };
export interface GameEvent {
  id: ID;
  runId: ID;
  type: string;
  storyMinute: number;
  occurredAtUtc: ISO8601;
  causationId?: ID;
  idempotencyKey: string;
  effects: Effect[];
}

export interface ModelCapabilities {
  chat: boolean;
  stream: boolean;
  structuredOutput: boolean;
  vision: boolean;
  stt: boolean;
  tts: boolean;
  supportedImageTypes: string[];
  supportedAudioTypes: string[];
  maxInputTokens?: number;
}
export interface ActorPromptContext {
  actorId: ID;
  personaText: string;
  knownFacts: Array<{ id: ID; description: string }>;
  visibleMessages: ChatMessage[];
  taskGoals: Array<{ taskId: ID; title: string }>;
  observableScene: string;
  playerIdentity: string;
  rulesSummary: string;
}
export interface AIAdapter {
  capabilities(): ModelCapabilities;
  /** Returns *untrusted* candidate action; do not directly persist as state. */
  proposeAction(context: ActorPromptContext, message: ChatMessage, signal?: AbortSignal): Promise<ActionProposal>;
  /** Narrate only effects that were committed by rules engine. */
  narrateCommitted(context: ActorPromptContext, events: GameEvent[], signal?: AbortSignal): AsyncIterable<string>;
}

export interface StoryPackInspection {
  packId: ID;
  version: string;
  title: string;
  compatible: boolean;
  errors: string[];
  warnings: string[];
}
export interface StoryPackService {
  inspect(input: Blob): Promise<StoryPackInspection>;
  install(input: Blob): Promise<{ packId: ID; packHash: string }>;
  list(): Promise<StoryPackInspection[]>;
}
export interface IdentityPolicy {
  authorize(runId: ID, playerRoleId: ID, capability: string): Promise<boolean>;
}
export interface RulesEngine {
  evaluateCondition(condition: Condition, state: GameState): boolean;
  adjudicate(state: GameState, proposal: ActionProposal): Promise<Verdict>;
  reconcileFate(state: GameState): Promise<GameEvent[]>;
}
export interface RuntimeEngine {
  createRun(packId: ID, playerRoleId: ID, seed?: string): Promise<GameState>;
  submitPlayerMessage(runId: ID, parts: MessagePart[], requestId: ID): Promise<ChatMessage[]>;
  advanceTime(runId: ID, toStoryMinute: number): Promise<GameEvent[]>;
  catchUp(runId: ID, nowUtc: ISO8601): Promise<{ events: GameEvent[]; pending: number }>;
  getState(runId: ID): Promise<GameState>;
  subscribe(runId: ID, handler: (event: GameEvent | ChatMessage) => void): () => void;
}
export interface SaveRepository {
  appendAtomic(runId: ID, events: GameEvent[], newState: GameState, messages: ChatMessage[]): Promise<void>;
  exportSave(runId: ID): Promise<Blob>;
  importSave(input: Blob): Promise<{ runId: ID; stateHash: string }>;
  createSnapshot(runId: ID): Promise<{ atRevision: number; sha256: string }>;
}
export interface MediaAdapter {
  inspectImage(asset: Blob, source: MessageProvenance, context: ActorPromptContext): Promise<{ caption: string; confidence?: number }>;
  transcribe(audio: Blob, language?: string): Promise<{ transcript: string }>;
  speak(text: string, voiceId: string): Promise<Blob>;
}
