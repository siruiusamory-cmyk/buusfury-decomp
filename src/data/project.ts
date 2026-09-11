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
    "The SDK can compose a new entity, its behavior, a gameplay trigger and an author-written message into one complete scene that plays in the original engine, and that message is no longer limited to the size of the line it replaces. The current frontier is fitting a long line onto the screen the game draws it on.",
  overallProgress: 90,
  overallProgressLabel: "≈ 90% COMPLETE",
  progressCaveat:
    "Progress is a directional project estimate. The milestones below are the authoritative measure of capability.",
  currentPhase: "AUTHOR_NEW",
  currentFrontierLabel: "CURRENT FRONTIER",
  existingContentState: "MATURE",
  blockerCode: "TEXT ON SCREEN",
  blockerTitle: "Fit authored text to the screen",
  blockerShort:
    "An authored message is no longer limited by the size of the line it replaces — the SDK moves it into free space and repoints the game's text table automatically. The remaining measured limit is display: a long line runs past the edges of the screen when the game draws it.",
  blockerParagraphs: [
    "The storage wall is gone. An authored message longer than the line it replaces is now written into verified free space, and the table entry the game uses to find that line is repointed at the new location, so the original engine renders the whole message through its ordinary lookup. The author writes a longer line and nothing else; no addresses, no flags, no request to relocate anything.",
    "Safety here rests on a measurement rather than an assumption. Before an entry may move, the SDK requires that exactly one four-byte-aligned word in the entire eight-megabyte game names that line's storage, and that the word is the entry's own table slot. A scan of every byte found exactly one such reference for the line used. Five of the game's 1,534 lines carry a second reference and are refused by that same rule — not by a hand-written list of exceptions, which would silently rot the first time the rule and the list disagreed.",
    "Two separate builds were played to confirm it, one carrying a 53-character message and one carrying 20, against an original line of 14. In both, the rewritten pointer resolved into the verified region and defeating the authored enemy rendered the relocated text. This reuses an existing text ID: creating entirely new entries in the text table is a different capability and is not claimed.",
    "What the second run exposed is the new frontier. The 20-character message still ran past the edges of the screen, because the game draws this kind of message centred in a large font and does not wrap it. That is a display constraint rather than a storage one, and the two were entangled until now — a message could not previously be long enough to reveal it.",
    "So the remaining question is no longer how much text can be stored, but how much can be shown at once. Nothing about the line's length in memory limits an author any more; what limits them is the width of a screen and the absence of wrapping. Neither the real character ceiling nor the cost of adding line breaks has been measured.",
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
      plainEnglish: "Combine a new entity, its behavior, a gameplay trigger, and an author-written message into one playable moment.",
      technical:
        "Confirmed, and it needed no new SDK code: the scene is one authored record plus one line of text in the project. A newly authored enemy was placed on an existing map, given its own behavior and script, tied to defeat, and made to display a message the author wrote. In the running game nothing authored happened while the enemy was alive, across 37 samples that each confirmed it was still present — most of them with it untouched, and the last two with it damaged but still standing; the instrument was separately confirmed live inside that same window. Defeating it ran the authored script and displayed SCENE CLEAR! on screen, and the operator then defeated it a second time, which reproduced the chain exactly. The entity, behavior and script are newly authored; the message is MODIFIED EXISTING text, overwriting a line the game already ships with, and is bounded by that line's 30-byte storage. No new text was allocated.",
      status: "complete",
    },
    {
      id: "author-new-text",
      title: "Author text without the retail slot-size limit",
      plainEnglish:
        "An authored message can now be longer than the line it replaces. The SDK moves it into verified free space and repoints the game's text table automatically.",
      technical:
        "Confirmed, and runtime-proven twice. A replacement longer than its original line is allocated into declared verified-writable space and the pointer-table entry that owns it is rewritten, so the original engine resolves the text through its normal lookup and renders the whole authored message. Relocation is gated per table by declared capability and per entry by measured ownership: an entry may move only when exactly one word-aligned reference in the whole 8 MiB image names its body, and that reference is its own table slot. A stride-1 scan found exactly one such word for the entry used. Five of the 1,534 entries carry a second reference and are refused by that rule rather than by any list. Two separate builds and play sessions, one with a 53-character message and one with 20 where the original line held 14, each showed the rewritten pointer resolving into the verified region and the authored script rendering the relocated text on defeat. This reuses an existing text ID; creating entirely new text-table IDs is not claimed.",
      status: "complete",
    },
    {
      id: "authored-text-display-width",
      title: "Fit authored text to the screen",
      plainEnglish:
        "A message can now be any length in storage, but a long line still runs past the edges of the screen when the game draws it.",
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
    { label: "COMPLETE AUTHORED SCENE", state: "done" },
    { label: "UNBOUNDED AUTHORED TEXT", state: "done" },
    { label: "AUTHORED TEXT FITS SCREEN", state: "current", marker: "↑ YOU ARE HERE" },
    { label: "PLAYABLE LOG1 CONTENT", state: "target" },
  ],
  breakthroughs: [
    {
      id: "first-newly-allocated-authored-text",
      title: "First newly allocated authored text resource",
      summary:
        "An overlength message written in a Webfoot SDK project was placed into new ROM space, connected through the game's own text table, and rendered by the original Buu's Fury engine.",
      technical:
        "The author writes a longer line and nothing else. The SDK encodes it, allocates it inside a region already verified as writable, rewrites the four-byte table entry that owns the original line, and the engine resolves the text through its normal lookup. Eligibility is measured, not assumed: an entry may relocate only when exactly one four-byte-aligned word in the whole eight-megabyte image names its storage and that word is the entry's own table slot. A scan of every byte found exactly one for the entry used; five of the 1,534 entries carry a second reference and are refused by that rule rather than by a list of indices. Two independent builds were played, carrying 53-character and 20-character messages against an original line of 14 characters, and both showed the rewritten pointer resolving into the verified region and the authored script rendering the relocated text on defeat. Builds are byte-identical between runs and the original game file is never modified. This reuses an existing text ID; the text table is not expanded and no new text ID is claimed. The 20-character run also showed the message running past the screen edges, which is a display limit rather than a storage one.",
    },
    {
      id: "first-complete-authored-scene",
      title: "First complete authored gameplay scene",
      summary:
        "A mod project built with Webfoot SDK now produces a complete playable encounter: a new enemy appears in the original Buu's Fury engine, is fought normally, and on defeat displays a message its author wrote.",
      technical:
        "The whole scene is one authored record plus one line of text in the project, and it required no new SDK code — every piece was already reachable through the ordinary extract, edit, validate and build steps. In the running game the authored enemy ran nothing authored for as long as it was alive, across 37 confirming samples — untouched for most of them, then damaged but still standing for the last two — with the instrument separately confirmed live in the same window. Defeating it ran the authored script and rendered SCENE CLEAR! on screen; the operator defeated it a second time and the chain reproduced identically. Builds are byte-identical between runs and the original game file is never modified. The entity, behavior and script are newly authored; the message is MODIFIED EXISTING text, overwriting an existing line in the bytes that line already occupies, so no new text was allocated and its length is bounded by that slot.",
    },
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
