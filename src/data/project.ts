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
    "The SDK can already make proven changes to existing game content. The current frontier is creating entirely new content that the original engine accepts and runs.",
  overallProgress: 70,
  overallProgressLabel: "≈ 70% COMPLETE",
  progressCaveat:
    "Progress is a directional project estimate. The milestones below are the authoritative measure of capability.",
  currentPhase: "AUTHOR_NEW",
  currentFrontierLabel: "CURRENT FRONTIER",
  existingContentState: "MATURE",
  blockerCode: "RUNTIME VALIDITY",
  blockerTitle: "Prove newly authored content runs in the engine",
  blockerShort:
    "The SDK now builds a real game file containing a newly authored entity. What is not yet proven is that the original engine accepts and runs it.",
  blockerParagraphs: [
    "The SDK now creates a new entity's real binary data, finds proven-safe space for it in the unmodified game, writes it, and rebuilds the game file. Exactly 48 bytes change, all of them intended, and repeated builds are identical.",
    "That is a structural result, not yet a playable one. The next measured step is running the built game and confirming the engine loads the new entity and behaves correctly with it.",
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
        "The built game file already contains the authored entity, with the map's object count and the pointer that reaches it updated. Whether the engine accepts it at runtime is a separate proof and is not yet claimed.",
      status: "current",
    },
    {
      id: "scripts-dialogue",
      title: "Author new scripts and dialogue",
      plainEnglish: "Give newly created content its own behavior, conditions, events, and text.",
      status: "next",
    },
    {
      id: "complete-scene",
      title: "Build a complete authored scene",
      plainEnglish: "Combine new entities, behavior, dialogue, and progression into a real Legacy of Goku scene.",
      status: "next",
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
    { label: "VERIFIED ROM CAPACITY", state: "current", marker: "↑ YOU ARE HERE" },
    { label: "NEW SCRIPTS + DIALOGUE", state: "next" },
    { label: "PLAYABLE LOG1 CONTENT", state: "target" },
  ],
  breakthroughs: [
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
