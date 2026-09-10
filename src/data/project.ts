export type MilestoneStatus = "complete" | "current" | "next" | "target";

export interface Milestone {
  id: string;
  title: string;
  plainEnglish: string;
  technical?: string;
  status: MilestoneStatus;
}

export interface Breakthrough {
  id: string;
  title: string;
  summary: string;
  technical?: string;
  date?: string;
  badge?: string;
  commit?: string;
}

export interface ProjectMetric {
  label: string;
  value: string;
  explanation?: string;
}

export interface Capability {
  label: string;
  title: string;
  description: string;
  state: string;
  status: MilestoneStatus;
}

export interface ProjectLink {
  label: string;
  url?: string;
}

export interface DependencyStep {
  label: string;
  state: "done" | "current" | "next" | "target";
  marker?: string;
}

export interface ProjectStatus {
  name: string;
  subtitle: string;
  tagline: string;
  description: string;
  overallProgress: number;
  overallProgressLabel: string;
  progressCaveat: string;
  currentPhase: string;
  currentFrontierLabel: string;
  existingContentState: string;
  blockerCode: string;
  blockerTitle: string;
  blockerShort: string;
  blockerParagraphs: string[];
  acceptanceTarget: string;
  definitionOfDone: string[];
  capabilities: Capability[];
  milestones: Milestone[];
  dependencyLadder: DependencyStep[];
  breakthroughs: Breakthrough[];
  metrics: ProjectMetric[];
  nav: { label: string; href: string }[];
  links: ProjectLink[];
  footerTagline: string;
  developmentStatus: string;
  disclaimer: string;
}

export const project: ProjectStatus = {
  name: "WEBFOOT SDK",
  subtitle: "Legacy of Goku authoring toolkit",
  tagline: "Building a real authoring toolkit for the Legacy of Goku engine.",
  description:
    "The SDK can create new entities and behavior that the original engine accepts, runs, and visibly renders on a deliberate gameplay trigger. The current frontier is combining those pieces into a complete authored scene.",
  overallProgress: 85,
  overallProgressLabel: "≈ 85% COMPLETE",
  progressCaveat:
    "Progress is a directional project estimate. The milestones below are the authoritative measure of capability.",
  currentPhase: "AUTHOR_NEW",
  currentFrontierLabel: "CURRENT FRONTIER",
  existingContentState: "MATURE",
  blockerCode: "COMPLETE SCENE",
  blockerTitle: "Build a complete authored scene",
  blockerShort:
    "The SDK can now author an entity, give it new behavior, and have that behavior run at a deliberate gameplay moment the author chooses. The remaining measured limit is scale: each of those pieces has been proven one at a time, not composed into a single authored scene.",
  blockerParagraphs: [
    "An author now declares a trigger alongside a behavior, and the engine honours it. Defeating the newly authored enemy ran the authored script and rendered the intended banner; the whole chain from the death callback to the visible effect completed inside eight frames.",
    "The negative control is what gives the trigger its meaning, and it sits in the same capture as the positive one. For about 7,400 frames the instrument sampled the authored enemy 124 times and recorded it present and alive every time, and across all of that it recorded no authored behavior start at all. One of those samples, at frame 8820, caught the enemy damaged but still alive, and still nothing authored ran. Defeating it started the behavior. A separate canonical control confirmed the same instrument detects a known kill, so that silence is real evidence rather than a dead channel.",
    "The trigger is deliberately narrow. It is proven for one enemy template on one verified game revision, and it is planning information rather than a new binary field: the engine relationship remains the ordinary placement descriptor pointer the SDK already writes.",
    "The next step is composition. Entities, behavior, visible effects and triggers each work in isolation; a real Legacy of Goku scene needs them combined, along with dialogue and progression, in one authored build.",
  ],
  acceptanceTarget:
    "Author playable Legacy of Goku content inside the real LOGII/Buu engine.",
  definitionOfDone: [
    "Webfoot SDK is the product, not a collection of reverse-engineering notes. Understanding the game only matters when it unlocks something an author can actually create.",
    "The acceptance test is straightforward: create newly authored Legacy of Goku content with the SDK, build the game, and successfully play it in the original engine.",
  ],
  capabilities: [
    {
      label: "EDIT",
      title: "Edit",
      description: "Change things that already exist.",
      state: "MATURE",
      status: "complete",
    },
    {
      label: "AUTHOR",
      title: "Author",
      description: "Create things that did not exist before.",
      state: "IN PROGRESS",
      status: "current",
    },
    {
      label: "PLAY",
      title: "Play",
      description: "Build newly authored LOG1 content and run it in the original engine.",
      state: "ACCEPTANCE TARGET",
      status: "target",
    },
  ],
  milestones: [
    {
      id: "modify-existing",
      title: "Modify existing content",
      plainEnglish: "Change something that already exists in the game.",
      status: "complete",
    },
    {
      id: "runtime-proof",
      title: "Prove the change in-game",
      plainEnglish:
        "Build the modified game and verify that the running game behaves exactly as predicted.",
      technical:
        "Wolf HP changed 175 → 1 through the SDK. Exactly one ROM byte changed. A wolf already loaded in a savestate still took four hits; newly spawned wolves died in one hit. This completed the first SDK → ROM → running-game proof.",
      status: "complete",
    },
    {
      id: "describe-entity",
      title: "Describe a new entity",
      plainEnglish: "Represent an entity that does not exist in the original game data.",
      technical: "Authored placement declarations now exist and serialize deterministically.",
      status: "complete",
    },
    {
      id: "complete-object-model",
      title: "Model the complete map object list",
      plainEnglish: "Understand every object the engine actually considers part of each map.",
      technical:
        "The corrected Buu census covers 1,898 engine-owned slots: 1,559 placement-family records and 339 sibling-family objects across 268 maps. The previous 1,442-placement census was incomplete.",
      status: "complete",
    },
    {
      id: "expand-object-list",
      title: "Expand the map object list",
      plainEnglish: "Increase the number of objects a map can contain.",
      technical:
        "An authored map change derives the count transition, such as 2 → 3, instead of exposing an arbitrary raw count edit.",
      status: "complete",
    },
    {
      id: "relocate-object-list",
      title: "Relocate the expanded object list",
      plainEnglish: "Move the larger list somewhere else without breaking the map's connection to it.",
      technical:
        "Evidence-based reference safety makes all 268 qualifying map object arrays relocatable under one rule, without hardcoded map exceptions.",
      status: "complete",
    },
    {
      id: "materialize-entity",
      title: "Materialize and connect the new entity",
      plainEnglish: "Create the actual new object data and make the map's new slot point to it.",
      technical:
        "An authored placement now becomes a real allocatable anchor holding the production codec's own bytes, and the map's newly created object slot holds a reference that resolves exactly to it.",
      status: "complete",
    },
    {
      id: "rom-capacity",
      title: "Establish verified ROM capacity",
      plainEnglish: "Provide proven-safe physical space for newly authored content.",
      technical:
        "A 256-byte region of the unmodified game is now verified writable and declared in the SDK profile, established by a check that also proves it detects the game's real structures. The whole authoring chain completes against the unmodified game and produces a built game file.",
      status: "complete",
    },
    {
      id: "runtime-validity",
      title: "Prove new entity in-game",
      plainEnglish:
        "Build the authored ROM and verify that the original engine actually loads and runs the newly created entity.",
      technical:
        "Confirmed. The built game file was run in the original engine, which read the authored object count and the relocated pointer list, resolved the new slot to the authored entity, and instantiated it. The new entity was observed in the running game.",
      status: "complete",
    },
    {
      id: "scripts-dialogue",
      title: "Attach and execute behavior",
      plainEnglish:
        "Give a newly authored entity an explicit engine behavior and prove the original game executes it.",
      technical:
        "Confirmed. The SDK assigns an existing behavior to a newly authored entity through its normal build path, and the original engine was observed executing it: the program counter reached the script handler five times in one session, each time carrying the authored behavior pointer and its script, with the interpreter entered on the same frame. A control build differing in exactly one word, with the same entity type, reached the handler zero times while the same instrument recorded other scripts running throughout.",
      status: "complete",
    },
    {
      id: "author-new-behavior",
      title: "Author new behavior",
      plainEnglish:
        "Create executable behavior content that did not exist in the original game and have the original engine run it.",
      technical:
        "Confirmed. The SDK writes a new behavior record and a new script body into verified space, points the authored entity at the record and the record at the script, and the original engine executed it: the interpreter was entered three times with its read position inside the newly allocated script body, the authored bytes present at that position each time, dispatched from the authored record. That byte sequence occurs zero times in the original game, and a control build contains neither structure. The script computes and discards a value, so no visible effect is claimed.",
      status: "complete",
    },
    {
      id: "gameplay-effect",
      title: "Make authored behavior affect gameplay",
      plainEnglish:
        "Newly authored behavior can intentionally invoke the original engine and produce a visible result.",
      technical:
        "Confirmed. An authored script invoked native slot 178 with text 1525 at X=120, Y=105. Runtime tracing captured the authored cursor, native opcode, selected handler and exact arguments; the next frames visibly rendered MATCH 2 FIGHT!. The same authored script without the native invocation ran but showed no banner.",
      status: "complete",
    },
    {
      id: "behavior-trigger",
      title: "Control when authored behavior runs",
      plainEnglish:
        "Newly authored behavior can now be tied to a deliberate, repeatable gameplay trigger instead of relying on an uncontrolled engine dispatch.",
      technical:
        "Confirmed. An author declares a trigger alongside the behavior, and the engine ran the authored script only when the player satisfied it. One capture holds both halves. For about 7,400 frames the authored enemy was sampled 124 times and found present and alive every time, and nothing authored ran; one sample at frame 8820 caught it damaged but still alive, and nothing authored ran then either. Defeating that same enemy produced the whole chain inside eight frames: the death callback carrying the authored actor at zero HP, the authored descriptor, the authored script, native slot 178 with the intended arguments, then the visible banner. The chain reproduced from a separate load, and a canonical control run confirmed the same instrument detects a known kill.",
      status: "complete",
    },
    {
      id: "complete-scene",
      title: "Build a complete authored scene",
      plainEnglish: "Combine new entities, behavior, dialogue, and progression into a real Legacy of Goku scene.",
      status: "current",
    },
    {
      id: "playable-log1",
      title: "Playable LOG1 content in the real engine",
      plainEnglish: "Build and play newly authored Legacy of Goku content using the original Webfoot game engine.",
      technical: "This is the mandatory acceptance target for Webfoot SDK.",
      status: "target",
    },
  ],
  dependencyLadder: [
    { label: "NEW ENTITY DESCRIPTION", state: "done" },
    { label: "COMPLETE MAP OBJECT MODEL", state: "done" },
    { label: "EXPANDED OBJECT LIST", state: "done" },
    { label: "SAFE RELOCATION", state: "done" },
    { label: "MATERIALIZE + CONNECT ENTITY", state: "done" },
    { label: "VERIFIED ROM CAPACITY", state: "done" },
    { label: "NEW ENTITY RUNS IN ENGINE", state: "done" },
    { label: "ATTACHED BEHAVIOR EXECUTES", state: "done" },
    { label: "AUTHORED SCRIPT EXECUTES", state: "done" },
    { label: "GAMEPLAY-EFFECT ACTION", state: "done" },
    { label: "AUTHORED BEHAVIOR TRIGGER", state: "done" },
    { label: "COMPLETE AUTHORED SCENE", state: "current", marker: "↑ YOU ARE HERE" },
    { label: "PLAYABLE LOG1 CONTENT", state: "target" },
  ],
  breakthroughs: [
    {
      id: "first-controlled-authored-event",
      title: "First controlled authored gameplay event",
      summary:
        "Webfoot SDK tied newly authored behavior to a deliberate gameplay condition and the original Buu's Fury engine executed it on command.",
      technical:
        "Defeating the authored enemy ran the authored script within eight frames: the death callback carried the authored actor at zero HP, the authored descriptor reached the authored script, native slot 178 received text 1525 at X=120, Y=105, and the banner appeared. In the same capture, leaving that enemy alive produced no dispatch and no banner across 124 samples that each confirmed it was still there and still alive, so the negative result is a measured absence rather than a silent instrument. A canonical kill in a separate run proved the death channel detects a known event.",
    },
    {
      id: "first-visible-authored-behavior",
      title: "First visible authored behavior",
      summary:
        "Webfoot SDK authored new behavior that intentionally caused a visible gameplay effect in the original Buu's Fury engine.",
      technical:
        "The authored script called native slot 178 with an existing text record and new screen coordinates. The engine reached the exact authored bytes and handler arguments, then rendered MATCH 2 FIGHT! on screen; an omitted-native control ran without the banner.",
    },
    {
      id: "runtime-proven-new-behavior",
      title: "First runtime-proven new behavior",
      summary:
        "Webfoot SDK created new executable behavior data that did not exist in the original game, attached it to a newly authored entity, and the original Buu's Fury engine executed it.",
      technical:
        "The interpreter entered the exact newly allocated 7-byte script body three times at runtime, dispatched from a newly written behavior record, with the authored bytes present at the interpreter's read position each time. That byte sequence occurs zero times in the original game and a control build contains neither structure. The script deliberately computes and discards a value, so no visible gameplay effect is claimed.",
    },
    {
      id: "runtime-proven-authored-entity",
      title: "First runtime-proven authored entity",
      summary:
        "Webfoot SDK created a map entity that did not exist in the original game, built it into Buu's Fury, and the original engine successfully loaded and instantiated it.",
      technical:
        "The engine read the authored fifth object slot and instantiated the clone from newly allocated ROM data. Exactly 56 bytes differ from the unmodified game, and the original file is never touched. The new entity is a copy of an existing one; it does not yet have behavior of its own.",
    },
    {
      id: "authored-rom-materialization",
      title: "First canonical AUTHOR_NEW ROM build",
      summary:
        "The SDK produced a deterministic Buu's Fury build containing genuinely new authored map data using verified writable space.",
      technical:
        "A 256-byte region of the unmodified game is verified writable and declared in the SDK profile. Materializing the authored entity requests 44 bytes of it, and exactly 48 bytes change across the whole game file. Repeated builds are byte-identical and the original game file is never modified.",
    },
    {
      id: "authored-body-materialization",
      title: "Authored entity body materialization",
      summary:
        "The SDK can now turn a newly authored placement into real binary data, allocate it, and connect the map's new object slot to it when verified space is available.",
      technical:
        "The authored body and the expanded pointer array are allocated independently, and the map's new slot resolves exactly to the authored body's address.",
    },
    {
      id: "safe-relocation",
      title: "Safe relocation of map object arrays",
      summary: "Expanded map object data can now be moved safely while preserving the map's connection to it.",
      technical: "268 map object arrays independently satisfy the evidence-backed relocation rule.",
    },
    {
      id: "complete-map-model",
      title: "Complete map object model",
      summary: "The SDK now follows the same map object counts as the game itself.",
      technical:
        "1,898 engine-owned slots: 1,559 placement-family objects and 339 sibling-family objects. The previous census reached 1,442 placements.",
    },
    {
      id: "map-count-writes",
      title: "Map-count writes",
      summary: "When a project adds another map object, the SDK derives the game's new object count safely.",
      technical: "Count changes follow authored list growth instead of accepting an arbitrary byte value.",
    },
    {
      id: "authored-placement",
      title: "Authored placement support",
      summary: "Projects can now describe placements that did not exist in the original game data.",
      technical: "Authored declarations have stable semantic identity and deterministic serialization.",
    },
    {
      id: "first-proof",
      title: "First runtime-proven SDK modification",
      summary: "A change made through the SDK produced exactly the predicted result in the running game.",
      technical:
        "Wolf HP 175 → 1; one ROM byte changed; newly spawned wolves changed from four-hit kills to one-hit kills.",
      badge: "FIRST PROOF",
    },
  ],
  metrics: [
    { label: "Map-owned object slots", value: "1,898" },
    { label: "Placement-family objects", value: "1,559" },
    { label: "Sibling-family objects", value: "339" },
    { label: "Maps with placements", value: "268" },
    { label: "Historical placement IDs preserved", value: "1,442" },
    { label: "Canonical no-op rebuild", value: "BYTE-IDENTICAL" },
    { label: "Canonical ROM during builds", value: "IMMUTABLE" },
  ],
  nav: [
    { label: "STATUS", href: "status" },
    { label: "QUESTLINE", href: "questline" },
    { label: "BREAKTHROUGHS", href: "breakthroughs" },
    { label: "ABOUT", href: "about" },
  ],
  links: [
    { label: "GitHub" },
    { label: "Documentation" },
    { label: "Project notes" },
  ],
  footerTagline:
    "A toolkit for authoring Legacy of Goku content against the actual LOGII/Buu engine.",
  developmentStatus: "ACTIVE DEVELOPMENT",
  disclaimer:
    "Independent fan development project. Not affiliated with Webfoot Technologies or the relevant game/IP rights holders.",
};

function validateProjectStatus(value: ProjectStatus): void {
  if (!Number.isFinite(value.overallProgress) || value.overallProgress < 0 || value.overallProgress > 100) {
    throw new Error("Project progress must be a finite number from 0 through 100.");
  }

  const currentMilestones = value.milestones.filter(({ status }) => status === "current");
  if (currentMilestones.length !== 1) {
    throw new Error(`Project questline must have exactly one current milestone; found ${currentMilestones.length}.`);
  }

  if (!value.blockerTitle.trim()) {
    throw new Error("Project status must include a current blocker title.");
  }

  if (!value.acceptanceTarget.trim() || !value.milestones.some(({ status }) => status === "target")) {
    throw new Error("Project status must include an acceptance target and a target milestone.");
  }
}

validateProjectStatus(project);

export const statusMeta: Record<MilestoneStatus, { icon: string; label: string }> = {
  complete: { icon: "✓", label: "COMPLETE" },
  current: { icon: "◆", label: "CURRENT" },
  next: { icon: "○", label: "NEXT" },
  target: { icon: "★", label: "TARGET" },
};
