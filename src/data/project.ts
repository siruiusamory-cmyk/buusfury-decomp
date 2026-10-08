import capabilityRegistry from "./capabilities.json";

export type MilestoneStatus = "complete" | "current" | "next" | "target";

export type CapabilityState = "shipped" | "missing";

export interface Milestone {
  id: string;
  title: string;
  plainEnglish: string;
  technical?: string;
  status: MilestoneStatus;
  openItems?: string[];
}

export interface Breakthrough {
  id: string;
  title: string;
  summary: string;
  technical?: string;
  date?: string;
  badge?: string;
  commit?: string;
  recent?: boolean;
}

export interface ProjectMetric {
  label: string;
  value: string;
  explanation?: string;
  group: string;
  strip?: boolean;
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

export interface BuildoutItem {
  key: string;
  title: string;
  detail: string;
  state: CapabilityState;
}

export interface BuildoutFamily {
  key: string;
  label: string;
  title: string;
  items: BuildoutItem[];
}

export interface Buildout {
  label: string;
  title: string;
  blurb: string;
  families: BuildoutFamily[];
}

export interface FrontierStep {
  kind: "near" | "gated" | "horizon";
  title: string;
  detail: string;
}

export interface StateFact {
  label: string;
  value: string;
}

export interface Figure {
  src: string;
  width: number;
  height: number;
  alt: string;
  title: string;
  caption: string;
  facts: string[];
}

export interface ProjectStatus {
  name: string;
  tagline: string;
  description: string;
  progressCaveat: string;
  currentPhase: string;
  blockerTitle: string;
  blockerShort: string;
  blockerParagraphs: string[];
  acceptanceTarget: string;
  definitionOfDone: string[];
  milestones: Milestone[];
  dependencyLadder: DependencyStep[];
  buildout: Buildout;
  frontier: FrontierStep[];
  stateFacts: StateFact[];
  breakthroughs: Breakthrough[];
  metrics: ProjectMetric[];
  figures: Figure[];
  nav: { label: string; href: string }[];
  links: ProjectLink[];
  footerTagline: string;
  developmentStatus: string;
  disclaimer: string;
  assetPolicy: string;
}

export type CapabilityProof = "runtime" | "application";

const PROOF_LEVELS: readonly CapabilityProof[] = ["runtime", "application"];

interface RegistryFamily {
  id: string;
  label: string;
  title: string;
}

interface RegistryCapability {
  id: string;
  family: string;
  title: string;
  state: CapabilityState;
  detail: string;
  limits: string[];
  surface?: string;
  proof?: CapabilityProof;
  evidence: string;
  measurements?: Record<string, number>;
}

interface RegistryResearchNote {
  id: string;
  statement: string;
  contributesTo: string[];
  doesNotConfer: string;
}

interface CapabilityRegistry {
  schemaVersion: number;
  track: {
    label: string;
    title: string;
    capabilityTotal: number;
    blurb: string;
  };
  families: RegistryFamily[];
  capabilities: RegistryCapability[];
  researchOnly: RegistryResearchNote[];
}

const registry = capabilityRegistry as unknown as CapabilityRegistry;

function validateCapabilityRegistry(value: CapabilityRegistry): void {
  if (value.schemaVersion !== 1) {
    throw new Error(`Unsupported capability registry schema version: ${value.schemaVersion}.`);
  }

  const familyIds = value.families.map((family) => family.id);
  const duplicateFamily = familyIds.find((id, index) => familyIds.indexOf(id) !== index);
  if (duplicateFamily) {
    throw new Error(`Capability family ids must be unique; "${duplicateFamily}" appears twice.`);
  }

  const capabilityIds = value.capabilities.map((capability) => capability.id);
  const duplicateCapability = capabilityIds.find(
    (id, index) => capabilityIds.indexOf(id) !== index,
  );
  if (duplicateCapability) {
    throw new Error(`Capability ids must be unique; "${duplicateCapability}" appears twice.`);
  }

  if (value.capabilities.length !== value.track.capabilityTotal) {
    throw new Error(
      `The registry declares ${value.track.capabilityTotal} capabilities but lists ` +
        `${value.capabilities.length}; update the denominator with the list.`,
    );
  }

  for (const family of value.families) {
    if (!value.capabilities.some((c) => c.family === family.id)) {
      throw new Error(`Capability family "${family.id}" lists no capabilities.`);
    }
  }

  for (const capability of value.capabilities) {
    const where = `capability "${capability.id}"`;

    if (!familyIds.includes(capability.family)) {
      throw new Error(`${where} names undeclared family "${capability.family}".`);
    }
    if (!/^[a-z][a-z0-9-]*$/.test(capability.id)) {
      throw new Error(`${where} has a malformed stable id.`);
    }
    if (capability.state !== "shipped" && capability.state !== "missing") {
      throw new Error(`${where} has state "${capability.state}", not "shipped" or "missing".`);
    }

    if (capability.state === "shipped") {
      if (!capability.surface?.trim() || !capability.proof || !PROOF_LEVELS.includes(capability.proof)) {
        throw new Error(
          `${where} is counted as shipped without the editor surface and a known proof level ` +
            `that separate a product capability from a research result.`,
        );
      }
    } else if (capability.surface || capability.proof) {
      throw new Error(
        `${where} is not shipped and must not claim an editor surface or a proof level.`,
      );
    }
  }

  for (const note of value.researchOnly) {
    if (capabilityIds.includes(note.id)) {
      throw new Error(`Research note "${note.id}" collides with a product capability id.`);
    }
    if (!note.statement.trim() || !note.doesNotConfer.trim()) {
      throw new Error(`Research note "${note.id}" must state its fact and what it does not confer.`);
    }
    for (const target of note.contributesTo) {
      if (!capabilityIds.includes(target)) {
        throw new Error(`Research note "${note.id}" contributes to unknown capability "${target}".`);
      }
    }
  }
}

validateCapabilityRegistry(registry);

function capabilityCount(capabilityId: string, name: string): number {
  const declared = registry.capabilities
    .find((capability) => capability.id === capabilityId)?.measurements?.[name];
  if (typeof declared !== "number") {
    throw new Error(`Capability "${capabilityId}" does not declare the ${name} measurement.`);
  }
  return declared;
}

const mapsViewable = capabilityCount("map-browser", "mapsViewable");
const layoutEditableMaps = capabilityCount("layout", "editableMaps");
const layoutReadOnlyMaps = capabilityCount("layout", "readOnlyMaps");
const transitionRecords = capabilityCount("warps", "transitionRecords");

const buildout: Buildout = {
  label: registry.track.label,
  title: registry.track.title,
  blurb: registry.track.blurb,
  families: registry.families.map((family) => ({
    key: family.id,
    label: family.label,
    title: family.title,
    items: registry.capabilities
      .filter((capability) => capability.family === family.id)
      .map((capability) => ({
        key: capability.id,
        title: capability.title,
        detail: capability.detail,
        state: capability.state,
      })),
  })),
};

export const project: ProjectStatus = {
  name: "WEBFOOT SDK",
  tagline: "A modding SDK and desktop editor for the Webfoot Dragon Ball Z GBA games.",
  description:
    "A modding toolkit and desktop editor for the three Webfoot Dragon Ball Z GBA" +
    " games. The engine-archaeology programme that built it is finished, and product" +
    " development continues one editor capability at a time against the verified" +
    " resource corpus.",
  progressCaveat:
    "The percentage above is counted from the capability list below, so it moves when a" +
    " capability does. It is a count of editor capabilities, not an estimate.",
  currentPhase: "DRAGONBYTE Z BUILDOUT",
  blockerTitle: "Reach a v1.0 release candidate",
  blockerShort:
    "Map authoring has shipped and the capability list is complete. Every capability" +
    " in the fixed registry is now reachable from DragonByte Z: the terminal one" +
    " composes the map table, a map root, its layers, chunks and connections into a" +
    " new playable area, and a driven session watched the retail engine transition" +
    " into it and back out. Nothing is missing any more. The remaining work is the" +
    " release-candidate phase - creator experience, recovery, packaging and the" +
    " end-to-end dogfood gate - and it has not started.",
  blockerParagraphs: [
    "Map editing is complete, and the capability list says so. Phase 2 covered the four" +
    " map capabilities in order: tile painting, chunk creation, map resizing with layer" +
    " authoring, and finally warps and connections. A transition can now be retargeted" +
    " through the project, a transition the image does not contain can be authored" +
    " under its own durable identity and built above the end of the original image, and" +
    " every supported transition is drawn on the map as the region that triggers it," +
    " where a click selects it and a drag moves it as one undoable gesture. A" +
    " human-operated run confirmed that the retail engine consumes an authored" +
    " transition, so the map surfaces are proven rather than planned.",
    "Graphics import is the first capability of the graphics phase and it has shipped." +
    " An extracted sprite asset's PNG is the authored source: edit it, validate, build," +
    " and the retail engine renders the authored pixels. A re-encoded payload that" +
    " still fits the slot the original occupied is written in place; one that does not" +
    " is placed by the production allocator above the original end of the image, with" +
    " every confirmed reference to it rewritten in the same transaction. A" +
    " human-operated run proved both halves, including that the engine follows a" +
    " rewritten reference into expanded storage.",
    "New sprite, animation and frame authoring has shipped as well. The Graphics tab's" +
    " Authored sprite surface creates the project's one new actor-sprite identity: the" +
    " donor whose proven composition shape every frame keeps, the sheet each animation" +
    " slot draws from, and the existing object slot the appended actor starts its" +
    " behaviour from. It refuses any field the build would refuse and writes" +
    " sprites/sprites.toml, the same document the ordinary build consumes, and a" +
    " ROM-gated build of the surface's own document authors the identity and actor the" +
    " runtime record resolved. The engine observation itself covers the mechanism: the" +
    " recorded runtime document carries a neighbouring sibling slot's data-pointer word" +
    " and the surface carries the chosen slot's own, in a field whose meaning is" +
    " unresolved, so the two images are not byte-identical and the capability is" +
    " registered at application proof. Piece and OAM composition, frame geometry and" +
    " frame timing are outside the modelled contract, and the surface states that where" +
    " it is offered rather than pretending otherwise.",
    "Appearance authoring has shipped as well, and it was the capability research had to" +
    " settle first. The table's record count is three compiled loop bounds with no" +
    " terminator, so growth is by re-emission: the build moves the whole table above the" +
    " image's end and rewrites the five literal words and three count bounds that reach" +
    " it. The roster structure the engine builds from the seen flags is relocated with" +
    " it, all twenty-nine compiled statements of its layout restated for the supported" +
    " maximum of 240 records against the 232 the image has. A driven session then watched the retail search return an authored record" +
    " at a post-canonical index for a retail actor, and the Scouter's own character" +
    " screen displayed the authored data for that actor - an object whose retail record" +
    " reads \"Fighter\" and \"This is a martial artist from the Other World\" showed the" +
    " authored name \"Goku\" and the authored description instead. Taking over a sprite" +
    " identity the retail table already uses is an explicit, default-off choice per" +
    " definition, because that redirection is real and the build refuses a takeover" +
    " nobody asked for.",
    "The capability list is complete: all 24 capabilities in the fixed registry are" +
    " shipped and reachable from DragonByte Z. The remaining work is the" +
    " release-candidate phase - creator experience, recovery, packaging and the" +
    " end-to-end dogfood gate - and it has not started.",
  ],
  acceptanceTarget:
    "Author playable Legacy of Goku content inside the real LOGII/Buu engine.",
  definitionOfDone: [
    "Webfoot SDK is the product, not a collection of reverse-engineering notes. Understanding the game only matters when it unlocks something an author can actually create.",
    "The acceptance test is straightforward: create newly authored Legacy of Goku content with the SDK, build the game, and successfully play it in the original engine.",
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
        "Confirmed. The SDK assigns an existing behavior to a newly authored entity through its normal build path, and the original engine was observed executing it: the program counter reached the script handler five times in one session, each time carrying the authored behavior pointer and its script, with the interpreter entered on the same frame. The handler entry is attributable to the authored content: the same instrument recorded zero entries without it, while other scripts continued to run.",
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
        "Confirmed. An author declares a trigger alongside the behavior, and the engine ran the authored script only when the player satisfied it. One capture holds both halves. Nothing authored ran while the enemy was alive: 124 samples found it present and alive, most of them with it untouched and the rest with it damaged but still standing, and none of them dispatched the authored behavior. Defeating that same enemy produced the whole chain inside eight frames: the death callback carrying the authored actor at zero HP, the authored descriptor, the authored script, native slot 178 with the intended arguments, then the visible banner. The chain reproduced from a separate load, and a canonical control run confirmed the same instrument detects a known kill.",
      status: "complete",
    },
    {
      id: "complete-scene",
      title: "Build a complete authored scene",
      plainEnglish: "Combine a new entity, its behavior, a gameplay trigger, and an author-written message into one playable moment.",
      technical:
        "Confirmed, and it needed no new SDK code: the scene is one authored record plus one line of text in the project. A newly authored enemy was placed on an existing map, given its own behavior and script, tied to defeat, and made to display a message the author wrote. In the running game nothing authored happened while the enemy was alive, including while it stood damaged. Defeating it ran the authored script and displayed SCENE CLEAR! on screen, and a second defeat reproduced the chain exactly. The entity, behavior and script are newly authored; the message is MODIFIED EXISTING text, overwriting a line the game already ships with, and is bounded by that line's 30-byte storage. No new text was allocated.",
      status: "complete",
    },
    {
      id: "author-new-text",
      title: "Author text without the retail slot-size limit",
      plainEnglish:
        "An authored message can now be longer than the line it replaces. The SDK moves it into verified free space and repoints the game's text table automatically.",
      technical:
        "Confirmed, and runtime-proven twice. A replacement longer than its original line is allocated into declared verified-writable space and the pointer-table entry that owns it is rewritten, so the original engine resolves the text through its normal lookup and renders the whole authored message. Relocation is gated per table by declared capability and per entry by measured ownership: an entry may move only when exactly one word-aligned reference in the whole 8 MiB image names its body, and that reference is its own table slot. For the entry used, exactly one word in the image names its body. Five of the 1,534 entries carry a second reference and are refused by that rule rather than by any list. Two separate builds and play sessions, one with a 53-character message and one with 20 where the original line held 14, each showed the rewritten pointer resolving into the verified region and the authored script rendering the relocated text on defeat. This reuses an existing text ID; creating entirely new text-table IDs is not claimed.",
      status: "complete",
    },
    {
      id: "authored-text-display-width",
      title: "Identify the remaining display-width limit",
      plainEnglish:
        "A message can be any length in storage, and a long line runs past the edges of the screen when the game draws it centred without wrapping.",
      technical:
        "Measured. Storage length no longer bounds an authored message; the remaining limit on this particular message style is display width, because the engine draws it centred in a large font with no wrapping. The character ceiling and the cost of adding line breaks are not yet measured. This is a known constraint of one message style rather than the project's frontier.",
      openItems: [
        "The character ceiling for a centred message, and what adding line breaks would cost.",
      ],
      status: "complete",
    },
    {
      id: "find-any-text",
      title: "Find any line of text in the game",
      plainEnglish:
        "Search the whole game for the words a character actually says, including text the game keeps compressed and never stores in readable form.",
      technical:
        "Confirmed. The full-ROM atlas is complete and reproducible, and its text search now covers verified compressed resources as well as plain ones, reporting each with its own result shape. The acceptance phrase \"Good luck, Goku!\" appears nowhere in the game as plain text; it was located inside a verified compressed container at ROM address 0x087A04F0, beginning 0x132 bytes into the decoded stream. That offset is a derived position within the decompressed data — it is not a ROM address and is not claimed as a string boundary, because segmentation of the decoded stream is still unknown. Indexing is gated to structurally reachable containers: a blind compression probe round-trips 24,285 hits into roughly 68.7 MiB of decode noise, and indexing that would present false positives as text sources.",
      status: "complete",
    },
    {
      id: "ordinary-dialogue-consumer",
      title: "Find the code that displays ordinary conversation",
      plainEnglish:
        "Prove that the original dialogue engine follows a relocated compressed resource and displays authored words.",
      technical:
        "Confirmed. The existing selector-1 packed handle remained `0x02002641`; its table entry was changed from `0x087A04F0` to `0x08800000` in generated ROM expansion, and mGBA displayed \"Nice work, Goku!\" through the normal retail dialogue box. The rebuilt container is 17,932 bytes, exceeding its 16,856-byte retail allocation by 1,076 bytes.",
      status: "complete",
    },
    {
      id: "expanded-dialogue-authored",
      title: "Author an ordinary NPC line through the normal build",
      plainEnglish:
        "Rewrite a real NPC conversation line, build the game the normal way, and have the original engine show the new words.",
      technical:
        "Confirmed. An ordinary compressed NPC line was rebuilt so long it no longer fit its retail slot; the SDK placed the complete resource in generated ROM expansion space, repointed only that container's table word, and the retail Buu's Fury engine displayed the authored line in its normal dialogue box — runtime-observed in mGBA with the original packed handle and selector unchanged. The canonical 8 MiB ROM is never modified; the appended space is generated capacity, allocated through the same shared allocator every other domain uses.",
      status: "complete",
    },
    {
      id: "variable-length-dialogue",
      title: "Change how long an existing line is",
      plainEnglish:
        "Replace a line the game already contains with a longer or a shorter one. The tool reworks that line's own storage and every line stored after it, so the rest of the conversation still reads exactly as it did.",
      technical:
        "Confirmed. Replacing the goku-greeting record's 32 decoded bytes with a 72-byte line re-authored its durable handle from 0x02002641 to 0x04802641 — same decoded start, new length — grew the decoded container from 65,474 to 65,514 bytes, shifted the 443 records that follow it, and repointed all 470 ROM words the engine reads as handles, while the 15 occurrences of superseded values that are not handles were left untouched. The container repacked from 16,856 to 17,952 bytes and was placed in generated expansion by the production allocator. The retail engine displayed the complete 36-character line in its normal dialogue box, and the canonical 8 MiB ROM is unchanged.",
      status: "complete",
    },
    {
      id: "graphical-workbench",
      title: "Drive the SDK from a desktop tool",
      plainEnglish:
        "Do the whole find, inspect, build and run loop from a graphical application instead of the command line.",
      technical:
        "Confirmed. The Webfoot Workbench is a desktop GUI and a second client of the same SDK, with its own editor surfaces covering the full loop: search the atlas, inspect a record, edit the game's content, build the game, and run the build. The build panel refuses to write over the source ROM. Graphical dialogue editing is intentionally not part of this milestone.",
      status: "complete",
    },
    {
      id: "gui-dialogue-editing",
      title: "Edit dialogue inside the Workbench",
      plainEnglish:
        "Search a supported line in the desktop tool, edit it, then build and run it — all without touching the command line.",
      technical:
        "Confirmed. The Inspector resolves mapped semantic targets through the production authoring API, keeps original, saved and unsaved values distinct, validates before mutation, persists the normal project schema, invalidates stale validation and build state, and builds through the SDK's own validate and build entry points. The goku-greeting workflow was completed twice through the GUI and the retail engine displayed Nice work, Goku!; unsupported search results remain read-only.",
      status: "complete",
    },
    {
      id: "playable-scene-authoring",
      title: "Author a complete playable scene in Workbench",
      plainEnglish:
        "Bring entity, placement, script, and dialogue authoring together in the desktop tool so a whole playable scene can be built without hand-operating the SDK.",
      technical:
        "Confirmed and runtime-proven. The owner personally authored a complete playable NPC scene entirely through the desktop GUI: select map:0040, clone a type_0086 enemy-linked placement, configure the entity, assign an on_defeat behavior plus an authored show_centered_sprite_text script, then Validate, Build, and Launch. Defeating the NPC in the retail Buu's Fury engine displayed the authored banner in-game. No new reverse engineering was required; every capability was surfaced through the existing SDK.",
      status: "complete",
    },
    {
      id: "scene-authoring-breadth",
      title: "Reach and author more maps and targets",
      plainEnglish:
        "Make more maps reachable for authoring and testing, and expand the entity, behavior, and dialogue targets an author can place, so real remake content can be produced comfortably.",
      technical:
        "Confirmed and runtime-proven across maps. Workbench lists all 452 known maps with explicit support states, composes retail and authored placements in one scene view, follows semantic relationships without copied IDs, and reviews pending changes in author-facing language. The owner personally authored, built, launched, and interacted with a second playable scene on map:0041.",
      status: "complete",
    },
    {
      id: "content-workflow-ergonomics",
      title: "Make authoring comfortable for real production",
      plainEnglish:
        "Make the successful scene workflow easy to understand and efficient enough to use repeatedly for actual remake content.",
      technical:
        "Delivered. The multi-map semantic workspace keeps a scene's relationships together and reviews pending changes in author-facing language, and authoring now runs through direct visual selection instead of list-and-form interaction.",
      status: "complete",
    },
    {
      id: "rom-only-map-renderer",
      title: "Render complete retail maps directly from ROM",
      plainEnglish:
        "See a retail map's real tiles and complete layered layout without capturing memory from a running emulator.",
      technical:
        "Runtime and static evidence prove the delta-coded tile-selector stream, multi-container character assembly, animation-frame decoding, logical 32x32 layout chunks, and camera-relative circular screenblock storage. The SDK's render_map(rom, map_id) path reconstructs two validation maps deterministically from immutable ROM data and matches the normalized VRAM-backed oracle exactly, without per-map rules.",
      status: "complete",
    },
    {
      id: "map-placement-coordinate-contract",
      title: "Place map objects on the logical map",
      plainEnglish:
        "Use a placement's stored position as an exact X/Y pixel location on the map canvas, and convert a map-pixel move back into the engine's own record format.",
      technical:
        "Controlled authored-ROM runs proved both signed position halfwords copy exactly into the placement actor's Q8 coordinate fields. The actor's installed dispatch table then converts them to camera-relative X/Y values and its renderer packs them into OAM X/Y fields. The reversible authoring contract is signed low-halfword X and high-halfword Y map/world pixels, with an explicit signed-16 range guard; camera and sprite-anchor terms are presentation state.",
      status: "complete",
    },
    {
      id: "visual-editor-foundation",
      title: "Show and edit real game graphics visually",
      plainEnglish:
        "See the game's actual sprites, frames, animations, and palettes, select them by sight, and edit a colour.",
      technical:
        "Sprite browsing and palette recolouring are proven by the emitted image rather than an emulator run: the recolour was confirmed by rendering the built image. DragonByte Z renders supported retail maps through the SDK's ROM-only renderer and overlays neutral placement markers at the proven signed map-pixel coordinates. The owner used the map itself to select, add, and move an object, then built and confirmed the generated ROM in the retail Buu's Fury engine. The GUI stays a thin client over semantic scene and project APIs; it contains no map-format or direct-ROM-write logic.",
      status: "complete",
    },
    {
      id: "complete-resource-extraction",
      title: "Extract the complete resource library",
      plainEnglish:
        "Pull every map, tile, sprite, animation and frame the game uses out of your own" +
        " copy of the game and into ordinary reusable files.",
      technical:
        "The exporter walks the accepted engine graphs rather than scanning heuristically." +
        " 452 maps and 1,808 map-layer references are classified, 1,559 known graphical" +
        " layers are exported with zero unresolved, and the complete tile, chunk, sprite," +
        " animation, frame and graphics populations are written deterministically." +
        " Generation is exactly reproducible and the user's game file is never modified.",
      status: "complete",
    },
    {
      id: "resource-library-curation",
      title: "Organise the extracted resource library",
      plainEnglish:
        "Turn the complete but raw extraction into a clean, de-duplicated library that a" +
        " person can actually browse and navigate.",
      technical:
        "Complete. The exporter output was measured for redundancy and its navigation" +
        " improved while every structural fact it recorded was proved to still resolve:" +
        " the raw extraction is de-duplicated into a curated pack with ROM-derived and" +
        " neutral names and a complete curated-to-raw source map, and the canonical raw" +
        " library remains byte-for-byte untouched. No extraction, classification or" +
        " rendering behaviour changed.",
      status: "complete",
    },
    {
      id: "map-browser",
      title: "Browse every map from ROM in the desktop application",
      plainEnglish:
        "Open any of the game's maps in the editor and see its real layered layout, at" +
        " zoom, without a running emulator.",
      technical:
        "Complete. The Map Browser is a read-only surface over the production ROM-only" +
        " renderer: all 452 maps are listed and filterable by name or map id, each map's" +
        " graphical layers render from immutable ROM bytes, and a map-information panel" +
        " reports its id, dimensions, layer count and per-layer type. Maps and layers" +
        " outside the proven render form are shown read-only with the reason stated.",
      status: "complete",
    },
    {
      id: "chunk-authoring",
      title: "Create a new reusable map chunk",
      plainEnglish:
        "Create a new reusable map chunk, edit it from existing game tiles, place it in a" +
        " map, and have the retail engine load it from newly allocated ROM space.",
      technical:
        "Complete. A project-authored chunk is a new packed 32x32 screen-entry body with" +
        " its own durable identity, composed from the screen entries the template's layer" +
        " already draws and stored as a sparse delta over that template. It is independent" +
        " of its source, survives save and reopen, is materialized by the one production" +
        " allocator above the canonical image's end because no canonical region can hold" +
        " it, is selectable as a map paint brush, and resolves from semantic identity to a" +
        " physical address at build time. The retail engine was observed reading it there:" +
        " its own loaded layer record held the new address and its uploaded BG1 tilemap" +
        " carried the authored arrangement while the other three layers stayed" +
        " byte-identical. An authored chunk rearranges existing graphics only - no new" +
        " tiles, palettes or imported artwork - and is map-scoped, because its plane of" +
        " screen entries only resolves through the assembled character block of the map" +
        " it was composed against. Its body is larger than the image's only declared" +
        " free region, so the engine reads it from generated expansion above the" +
        " original ROM's end.",
      status: "complete",
    },
    {
      id: "playable-log1",
      title: "Playable LOG1 content in the real engine",
      plainEnglish: "Build and play newly authored Legacy of Goku content using the original Webfoot game engine.",
      technical:
        "This is the mandatory acceptance target for Webfoot SDK. Authoring entirely new" +
        " content remains the goal; it is now reached through the desktop editor rather" +
        " than being the organising priority for current tool development.",
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
    { label: "AUTHORED TEXT FITS SCREEN", state: "done" },
    { label: "ANY TEXT FINDABLE BY ITS WORDS", state: "done" },
    { label: "ORDINARY DIALOGUE DISPLAY PATH", state: "done" },
    { label: "EXPANDED DIALOGUE CAPACITY", state: "done" },
    { label: "AUTHORED ORDINARY NPC DIALOGUE", state: "done" },
    { label: "GENERATED-ROM RESOURCE RELOCATION", state: "done" },
    { label: "GRAPHICAL WORKBENCH", state: "done" },
    { label: "GUI DIALOGUE EDITING", state: "done" },
    { label: "PLAYABLE SCENE AUTHORING", state: "done" },
    { label: "SCENE AUTHORING BREADTH", state: "done" },
    { label: "CONTENT WORKFLOW ERGONOMICS", state: "done" },
    { label: "VISUAL GRAPHICS + PALETTE EDITING", state: "done" },
    { label: "ROM-ONLY MAP RENDERING", state: "done" },
    { label: "VISUAL MAP EDITOR", state: "done" },
    { label: "COMPLETE RESOURCE EXTRACTION", state: "done" },
    { label: "RESOURCE LIBRARY CURATION", state: "done" },
    { label: "MAP BROWSER", state: "done" },
    { label: "DRAGONBYTE Z FEATURES", state: "current" },
    { label: "ADVANCED AUTHORING / AUTHOR_NEW", state: "target" },
    { label: "PLAYABLE LOG1 CONTENT", state: "target" },
  ],
  buildout,
  stateFacts: [
    { label: "TARGET HARDWARE", value: "GBA · 240 × 160" },
    { label: "GAMES IN SCOPE", value: "Legacy of Goku · LoG II · Buu's Fury" },
  ],
  frontier: [
    {
      kind: "near",
      title: "Compose a frame's pieces into one displayed image",
      detail:
        "The accepted frame layout is an 8-byte header with 12-byte pieces, and the" +
        " reader and codec now read exactly that, so multipart frames are decoded and" +
        " exported. Compositing one frame's pieces into a single displayed image, and" +
        " replacing them, is the step that remains, together with authoring a frame's" +
        " own piece composition, geometry and timing.",
    },
    {
      kind: "horizon",
      title: "Creator experience and release",
      detail:
        "No capability is missing any more. What is left is the release-candidate"
        + " phase: engine limits shown before a build fails, recovery from" +
        " interrupted work, navigation between related resources, Run From Here," +
        " project migration, packaging and the end-to-end dogfood gate.",
    },
  ],
  breakthroughs: [
    {
      id: "roadmap-to-1-0-published",
      title: "The complete roadmap to 1.0 is published",
      summary:
        "The remaining path is public: the phases that lead to 100% feature" +
        " completeness, what each one adds, and the separate release gate that" +
        " follows it.",
      technical:
        "The tracked roadmap ordered the eight authoring capabilities that were" +
        " still missing when it was published, and states its dependencies, its" +
        " addressability strategy and its acceptance" +
        " project. The site derives every phase count from the same capability" +
        " registry the capability list uses, so the published plan cannot drift" +
        " from what the product can actually do.",
      recent: true,
    },
    {
      id: "variable-length-dialogue-authoring",
      title: "An existing line of dialogue can change length",
      summary:
        "Replace a line the game already contains with a longer or a shorter one." +
        " The tool reworks that line's own storage and every line stored after it," +
        " so the rest of the conversation still reads exactly as it did.",
      technical:
        "A 32-byte line was replaced by a 72-byte one: the tool re-authored the" +
        " record's durable handle, grew the decoded container, shifted the 443" +
        " records that follow it and repointed the 470 ROM words the engine reads" +
        " as handles, leaving 15 equal-valued words that are not handles untouched." +
        " The retail engine displayed the complete longer line, and the original" +
        " game file is unchanged.",
      recent: true,
    },
    {
      id: "production-allocator-expanded-space",
      title: "A production allocator, and authored data proven above 8 MiB",
      summary:
        "New content can be placed beyond the original image by an allocator that" +
        " records where it went and refuses to reuse it, and the original engine" +
        " has been observed consuming authored data from that expanded space.",
      technical:
        "A deterministic allocator reserves authorised spans in a generated 16 MiB" +
        " image, records their provenance, reopens them and prevents reuse; a real" +
        " compressed dialogue resource was placed at file offset 0x00800000 / ROM" +
        " address 0x08800000 and consumed by the retail engine. Only the domains a" +
        " feature has actually proven are claimed: the original 8 MiB image still" +
        " carries 256 bytes of verified free space, and expanded storage is not yet" +
        " proven for every resource family.",
      recent: true,
    },
    {
      id: "runtime-proven-chunk-creation",
      title: "Create a new map chunk and see the real game load it",
      summary:
        "You can now create a map chunk that did not exist before: duplicate one of the"
        + " chunks a map layer already draws, rearrange its tiles inside DragonByte Z,"
        + " save it, then paint a map cell with it. The change survives closing and"
        + " reopening, builds into a new game file, and the actual game draws it - from"
        + " space added beyond the end of the original game file.",
      technical:
        "A dominant chunk is a packed container declaring 0x800 bytes: 1,024"
        + " little-endian 16-bit screen entries, one 32x32 plane, with bits 0-9 the tile"
        + " ordinal, 10 and 11 the flips and 12-15 the palette bank. Every one of the"
        + " 3,745 chunk bodies the canonical image references is container kind 1, so an"
        + " authored body is emitted in that same kind rather than in the encoder's own."
        + " The authoring vocabulary is exactly the screen entries the template's own"
        + " layer already displays, so a new chunk rearranges the game's graphics and"
        + " adds none; the template is named by the layer's own 1-based chunk ordinal and"
        + " resolved against the canonical image only, so painting a cell can never"
        + " re-point a template. Project state is address-free: maps/chunks.toml holds"
        + " each chunk as an identity plus a sparse delta with the entry it replaced, and"
        + " a layout cell may hold either a canonical ordinal or a chunk identity - the"
        + " build allocates the body, resolves the identity to that address and writes"
        + " the cell reference. The canonical image's only declared free region is 256"
        + " bytes and a container is larger, so expansion above the 8 MiB end is required"
        + " rather than optional: the body was placed at file 0x00800000 / ROM address"
        + " 0x08800000 on a generated 16 MiB image, and in the canonical region exactly"
        + " three bytes changed, at the painted cell's pointer. Proven in the retail"
        + " engine, matched A/B with a real leave-and-re-enter rebuild in each run: the"
        + " engine's own loaded layer record was observed holding 0x08800000 where the"
        + " retail image holds the old chunk's address, and the engine's uploaded BG1"
        + " tilemap carried the authored arrangement in 593 of its 1,024 entries while"
        + " BG0, BG2 and BG3 stayed byte-identical. No new tiles, no new palettes, no"
        + " imported artwork, no resizing and no new layers; an authored chunk is"
        + " map-scoped, because its tile ordinals only mean anything through the map it"
        + " was composed against.",
      recent: true,
    },
    {
      id: "runtime-proven-map-growth",
      title: "Grow a map and see the new ground in the real game",
      summary:
        "You can now make a supported existing map bigger in DragonByte Z, or add a"
        + " supported visual layer to it, and see the result in the running game. The"
        + " added ground is initialized from graphics the map already uses, stored in"
        + " the project, and displayed by the retail engine - which previously could"
        + " not even reach that part of the map.",
      technical:
        "A supported dominant layer's chunk grid can be grown. The resize is top-left"
        + " anchored, so every existing cell keeps its coordinate and only the added"
        + " cells are initialized. A dominant layer record is exactly its 0x18-byte"
        + " header plus its 4-byte-per-cell chunk window and nothing else - measured"
        + " over all 1,516 canonical records, with live data immediately after the"
        + " window - so a grown grid cannot stay where it was: the record is re-emitted"
        + " whole above the original ROM's end and the map root's own layer-slot field"
        + " is repointed at it. The engine clamps its camera to the map's declared"
        + " extent, so a grow also raises that word; without it the added ground is"
        + " unreachable. Proven in the retail engine after a genuine leave-and-re-enter:"
        + " the engine's live layer record held the grown 2x1 grid and pointed the added"
        + " cell at the authored chunk, its camera reached 70 pixels past the retail"
        + " clamp, and at a matched camera the only pixels that differed from retail were"
        + " inside the added cell's band, with the layer underneath byte-identical.",
      recent: true,
    },
    {
      id: "runtime-proven-tile-painting",
      title: "Paint a map's layout and see it in the real game",
      summary:
        "You can now repaint the visible layout of an existing map in DragonByte Z -"
        + " choose a chunk the layer already uses, then click or drag it onto the map."
        + " The change is stored in the project, survives closing and reopening, builds"
        + " into a new game file, and shows up in the actual game.",
      technical:
        "The editable unit is the engine's own: one four-byte chunk-cell reference on a"
        + " dominant layer, pointing at an existing 256x256 chunk. No new chunk, no map"
        + " resizing, no layer creation. Painting is a semantic project edit"
        + " (maps/layout.toml, keyed map -> layer -> row-major cell -> 1-based chunk"
        + " ordinal) and joins the same single write plan as every other authored"
        + " content, so a build changes only the painted cells - on map:0040 that was"
        + " exactly two bytes at file 0x00292CA0, with the other 8,388,606 unchanged."
        + " Proven in the retail engine, matched A/B: the same savestate was loaded with"
        + " the retail image and with the authored derivative, and in EACH run the player"
        + " walked out of the area and back so the engine rebuilt the map from ROM - a"
        + " savestate alone restores the already-assembled background, so a capture taken"
        + " without a rebuild cannot tell the two ROMs apart, and the capture tool now"
        + " refuses to fire unless it has watched that leave-and-return and the rebuild"
        + " settle. 7,013 of 38,400 screen pixels differed, every one inside the painted"
        + " cell's own region, with a hard texture seam at that cell's boundary that the"
        + " retail frame does not have. Undo, redo, eyedropper and drag painting share one"
        + " history. Groundwork for this was the map-layout writer; warp and connection"
        + " editing shipped later as the fourth and final map-editing capability.",
      recent: true,
    },
    {
      id: "fixed-size-map-layout-write",
      title: "Map layout editing is a usable feature",
      summary:
        "A retail map's layout can now be edited from DragonByte Z: swap one chunk cell" +
        " for another chunk the same layer already uses, preview it, and save a new" +
        " game file that re-renders with the change.",
      technical:
        "On Buu's Fury map:0040, dominant layer 1 cell 0 was redirected to another" +
        " chunk already used by that layer. Exactly two ROM bytes changed within its" +
        " four-byte pointer; the changed 256-by-256-pixel region re-rendered through" +
        " the accepted map pipeline with 29,208 changed pixels, all inside that cell," +
        " while the layer's other three regions stayed pixel-identical. No-op and" +
        " inverse builds matched all 8,388,608 canonical bytes. The source ROM was not" +
        " modified. The Map Browser drives this over 341 of the 452 maps. Emulator" +
        " validation of the layout write itself was not performed; the application" +
        " round-trip was, by reopening its own emitted ROM through the provenance" +
        " manifest it wrote beside it.",
      recent: true,
    },
    {
      id: "complete-resource-extraction",
      title: "Complete resource extraction",
      summary:
        "Maps, map layers, tiles, chunks, sprites, animations, frames and their underlying" +
        " graphics can now be exported out of your own copy of the game into reusable" +
        " files.",
      technical:
        "The exporter walks the game's own structures instead of scanning heuristically:" +
        " 452 maps and 1,808 map-layer references classified, 1,559 known graphical layers" +
        " exported with zero unresolved, and complete tile, chunk, sprite, animation, frame" +
        " and graphics populations. Output is deterministic between runs, and the game" +
        " file is never modified. The single special-case terrain-field layer is" +
        " extracted too.",
      recent: true,
    },
    {
      id: "all-map-layers-classified",
      title: "Every known map layer classified",
      summary:
        "No map layer is left unexplained. All 1,808 map-layer references are structurally" +
        " classified, and every graphical layer among them is exported as an image.",
      technical:
        "Each layer reference is classified from the engine's own handler code and the" +
        " paths that reach its records, not from appearance. 1,559 graphical layers are" +
        " exported, 249 references are proven to draw nothing, and zero graphical layers" +
        " remain unresolved or silently omitted.",
      recent: true,
    },
    {
      id: "resource-library-curated",
      title: "The extracted library is organised and browsable",
      summary:
        "The complete but raw extraction is now a clean, de-duplicated, human-navigable" +
        " resource pack with ROM-derived and neutral names, and every structural fact it" +
        " records still resolves.",
      technical:
        "The curated pack is rebuilt deterministically from the raw extraction and" +
        " carries a complete curated-to-raw source map, so any curated entry can be" +
        " traced back to the structure it came from. The canonical raw library is left" +
        " byte-for-byte untouched. No extraction, classification or rendering behaviour" +
        " changed.",
      recent: true,
    },
    {
      id: "sprite-pipeline-reconstructed",
      title: "Sprite pipeline reconstructed",
      summary:
        "Sprite definitions, animation slots, directional frames, multipart pieces and" +
        " their graphics can all be exported and re-associated.",
      technical:
        "The exporter reads the count-bounded animation arrays and the frame/piece records" +
        " directly: 297 sprite definitions, 4,070 animation slots, 1,721 non-null animation" +
        " references, 10,980 frame records, 11,005 pieces, 21 multipart frames and 7,390" +
        " structured graphics containers. The accepted frame layout is an 8-byte header" +
        " with 12-byte pieces, and the shipped reader now reads it: multipart frames are" +
        " decoded and exported, though the editor still draws one piece per direction" +
        " slot because the composite path is not built yet.",
    },
    {
      id: "research-freeze-complete",
      title: "Engine archaeology and final synthesis complete",
      summary:
        "The broad reverse-engineering programme that underpinned the toolkit is finished," +
        " and its results are consolidated into canonical schemas.",
      technical:
        "The broad reverse-engineering programme is consolidated into canonical schemas," +
        " and every load-bearing result is recorded with its evidence and confidence." +
        " Further work is targeted and capability-driven rather than open-ended.",
    },
    {
      id: "visual-map-placement-authoring",
      title: "Direct visual placement editing on retail maps",
      summary:
        "DragonByte Z now renders a retail map from ROM as the primary authoring surface, where an author can select, add, inspect, and move supported objects directly on the map.",
      technical:
        "The workspace consumes the production ROM-only map renderer and the confirmed signed map-pixel placement transform. It uses neutral markers because placement-to-sprite identity remains unproven, persists movement through semantic project APIs, supports Undo/Redo, and builds through normal validation. The owner completed the visual workflow and confirmed the generated ROM places the authored object at the intended location in the retail Buu's Fury engine.",
    },
    {
      id: "semantic-multi-map-workspace",
      title: "Semantic scene authoring across multiple maps",
      summary:
        "Workbench now browses maps and related game content by semantic identity, keeps a scene's relationships together, previews pending changes, and has produced a second playable authored scene on a different map.",
      technical:
        "Runtime-proven on map:0041 after the earlier map:0040 scene. The owner selected the map, cloned and configured a supported entity, assigned behavior and a visible response, reviewed project changes, validated, built, launched, reached the map, and observed the authored interaction—without raw ROM addresses or project-file editing.",
    },
    {
      id: "scene-authored-through-workbench",
      title: "First complete playable scene authored entirely in the desktop tool",
      summary:
        "The project owner built a full playable NPC scene from start to finish inside Webfoot Workbench — choosing a map, placing an enemy, giving it behavior, a script, a defeat trigger, and an author-written message, then validating, building, and launching — with no Python, TOML, command line, or hex. Defeating the NPC in the original Buu's Fury engine showed the authored banner on screen.",
      technical:
        "Runtime-proven. The scene was authored on map:0040: clone a type_0086 enemy-linked placement, configure the entity, assign an on_defeat behavior plus an authored show_centered_sprite_text script, then Validate, Build, Launch, defeat the NPC, and observe the authored banner in the retail engine — every step through the GUI. No new reverse engineering was required; the capabilities were surfaced through the existing SDK. The proven scene is deliberately one authored record plus one line of text, which makes breadth the next frontier.",
    },
    {
      id: "first-usable-workbench",
      title: "First usable Webfoot Workbench",
      summary:
        "The SDK now has a desktop application. An author can search for a supported dialogue line, edit and validate it, build the game, and launch the result without using the command line.",
    },
    {
      id: "first-ordinary-authored-dialogue",
      title: "First ordinary NPC line authored through the normal build",
      summary:
        "A real NPC conversation line was rewritten in a Webfoot SDK project, built the ordinary way, and shown by the original Buu's Fury engine in its normal dialogue box — the first time an everyday compressed line has been replaced through the standard project build.",
    },
    {
      id: "first-expanded-rom-resource",
      title: "First authored resource proven from expanded ROM space",
      summary:
        "An authored line that no longer fit its original slot was placed into new, generated ROM space, selected by the game's own table, and displayed by the retail engine — the first authored resource proven to run from beyond the original ROM boundary, with the original game file left untouched.",
    },
    {
      id: "expanded-authored-dialogue",
      title: "Authored dialogue now crosses the original ROM boundary",
      summary:
        "A rebuilt compressed dialogue resource that no longer fits in the retail image was placed into generated expansion space, selected by the original table, and displayed by the retail engine.",
      technical:
        "The selector-1 container grew from its 16,856-byte retail allocation to 17,932 bytes. The SDK emitted a deterministic 16 MiB image, placed the complete payload at file offset 0x00800000 / ROM address 0x08800000, and changed only selector 1's table word. The record and packed handle remained unchanged. mGBA observed the handle and selector reach the relocated pointer, then displayed \"Nice work, Goku!\" in the ordinary dialogue box. The original 8 MiB ROM remains unchanged; appended bytes are generated capacity, not a retail free-space claim.",
    },
    {
      id: "compressed-text-searchable",
      title: "Every line of text in the game is now findable by its words",
      summary:
        "A line of dialogue that exists nowhere in the game as readable text was located by searching for the words themselves, inside the packed data that hides it. Searching the game for what a character says now works whether that line is stored plainly or compressed.",
      technical:
        "The full-ROM atlas is complete and reproducible, and its text search covers verified compressed resources alongside plain text runs, reporting each with its own result shape rather than flattening them together. The acceptance phrase \"Good luck, Goku!\" is absent from the game in every plaintext form. It was found inside a verified compressed container at ROM address 0x087A04F0, beginning 0x132 bytes into the decoded stream. That offset is a derived position within the decompressed data: there is no ROM address for the phrase, and no string boundary is claimed there — the run reads straight through neighbouring words with no delimiter, which is itself evidence that segmentation of the decoded stream is still unknown. Indexing is deliberately gated to structurally reachable containers; a blind compression probe round-trips 24,285 hits into roughly 68.7 MiB of decode noise, and indexing that would have presented false positives as genuine text sources. What this exposed is the next frontier: ordinary conversation is stored readably, but the game code that draws it on screen has not been identified or watched running.",
    },
    {
      id: "shop-scenario-structure",
      title: "Shop and scenario structure mapped",
      summary:
        "The way the game organises shop conversations is now materially understood, which is what narrowed the search for the code that displays ordinary dialogue.",
      technical:
        "Six known shop scenarios and 61 script targets, with the script framing confirmed as u16 next_script_index followed by u8 type across all of them. Every observed type value is accounted for; 17 targets carry plaintext payloads that can already be read. The dispatcher that reads the type byte accepts only two of the values and rejects the plaintext one, which places the consumer of that plaintext elsewhere in the engine — still unidentified, and never yet observed executing in a running game.",
    },
    {
      id: "buu-rom-bible",
      title: "Buu's Fury ROM Bible",
      summary:
        "A standalone reference covering what the project has established about the Buu's Fury game data, written for other people working on the same game and shared with the Legacy of Goku community on their Discord server. The reference document is not hosted on this site.",
    },
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
        "The whole scene is one authored record plus one line of text in the project, and it required no new SDK code: every piece was already reachable through the ordinary extract, edit, validate and build steps. In the running game the authored enemy ran nothing authored for as long as it was alive, including while it stood damaged. Defeating it ran the authored script and rendered SCENE CLEAR! on screen, and a second defeat reproduced the chain identically. Builds are byte-identical between runs and the original game file is never modified. The entity, behavior and script are newly authored; the message is MODIFIED EXISTING text, overwriting an existing line in the bytes that line already occupies, so no new text was allocated and its length is bounded by that slot.",
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
    { group: "Map editing", strip: true, label: "Maps viewable in the Map Browser", value: `${mapsViewable} / ${mapsViewable}` },
    { group: "Map editing", strip: true, label: "Maps exposing an editable layer", value: `${layoutEditableMaps} / ${mapsViewable}` },
    { group: "Map editing", strip: true, label: "Maps read-only, with the reason stated", value: `${layoutReadOnlyMaps} / ${mapsViewable}` },
    {
      group: "Map editing",
      strip: true,
      label: "Bytes changed by the proved layout write",
      value: "2",
      explanation: "Within one four-byte chunk pointer field, at file 0x00292CA0.",
    },
    {
      group: "Map editing",
      strip: true,
      label: "Pixels re-rendered in the changed cell",
      value: "29,208",
      explanation: "All inside the edited 256x256 region; the layer's other three regions were identical.",
    },
    {
      group: "Map editing",
      strip: true,
      label: "Reopening a ROM this feature wrote",
      value: "PROVENANCE-GATED",
      explanation: "Accepted only when a manifest proves the image is the canonical one plus declared, legal edits.",
    },
    {
      group: "Map editing",
      label: "Dominant-layer slots offering a second chunk",
      value: "1,093 / 1,516",
    },
    { group: "Corpus", strip: true, label: "Map layer references classified", value: "1,808 / 1,808" },
    { group: "Corpus", strip: true, label: "Unresolved graphical layers", value: "0" },
    {
      group: "Corpus",
      strip: true,
      label: "Curated resource library",
      value: "DETERMINISTIC",
      explanation: "Rebuilt from the raw extraction with a complete curated-to-raw source map; the raw library stays untouched.",
    },
    { group: "Corpus", label: "Maps extracted", value: "452" },
    { group: "Corpus", label: "Graphical map layers exported", value: "1,559" },
    { group: "Corpus", label: "Tile banks extracted", value: "187" },
    { group: "Corpus", label: "Individual tiles extracted", value: "47,857" },
    { group: "Corpus", label: "Map chunks extracted", value: "3,745" },
    { group: "Corpus", label: "Sprite definitions extracted", value: "297" },
    { group: "Corpus", label: "Animation slots extracted", value: "4,070" },
    { group: "Corpus", label: "Frame records extracted", value: "10,980" },
    { group: "Corpus", label: "Sprite pieces extracted", value: "11,005" },
    { group: "Corpus", label: "Structured sprite graphics extracted", value: "7,390" },
    { group: "Map objects", label: "Map-owned object slots", value: "1,898" },
    { group: "Map objects", label: "Placement-family objects", value: "1,559" },
    { group: "Map objects", label: "Sibling-family objects", value: "339" },
    { group: "Map objects", label: "Maps with placements", value: "268" },
    { group: "Map objects", label: "Historical placement IDs preserved", value: "1,442" },
    { group: "Integrity", strip: true, label: "Canonical no-op rebuild", value: "BYTE-IDENTICAL" },
    { group: "Integrity", strip: true, label: "Canonical image during builds", value: "IMMUTABLE" },
    {
      group: "Integrity",
      label: "Transition records read, anomalies",
      value: `${transitionRecords} / 0`,
      explanation: "Warp and connection records; the Warps mode lists and retargets them, and the map canvas draws each one's trigger region.",
    },
  ],
  figures: [
    {
      src: "dbz-map-browser.png",
      width: 1700,
      height: 1264,
      alt:
        "The DragonByte Z Maps editor in Browse mode showing Buu's Fury map:0040," +
        " Grand Kai's Planet: a searchable list of retail map names on the left, the" +
        " map rendered from ROM bytes in the middle, and the Inspector on the right" +
        " stating that the map is read-only until Layout mode is switched on.",
      title: "Maps editor",
      caption:
        "Map:0040 rendered from immutable ROM bytes, layer by layer. Every one of the" +
        ` ${mapsViewable} maps opens here without a running emulator.`,
      facts: [
        `${mapsViewable} maps viewable`,
        "Rendered from ROM, not captured from memory",
        "Read-only until Layout mode is switched on",
      ],
    },
    {
      src: "dbz-layout-editor.png",
      width: 305,
      height: 716,
      alt:
        "The DragonByte Z Inspector pane in the Maps editor's Layout mode for" +
        " map:0064, layer BG0, showing one staged paint on a 256x256 chunk cell, the" +
        " layer's 1x2 chunk grid, the cell's four-byte pointer field being changed in" +
        " place, and the map-structure list naming every layer's form beside the" +
        " resize, Create Chunk and Save As New ROM controls.",
      title: "Layout editing",
      caption:
        "Layout mode on map:0064, one 256x256 cell of dominant layer BG0. The staged" +
        " paint is a four-byte in-place cell write, and the map-structure list states" +
        " which layers may be changed and which stay read-only.",
      facts: [
        `${layoutEditableMaps} of ${mapsViewable} maps expose an editable layer`,
        "Brush drawn from the layer's own chunks",
        "Saved as a new ROM, with provenance",
      ],
    },
  ],
  nav: [
    { label: "Welcome", href: "status" },
    { label: "Progress", href: "progress" },
    { label: "Latest posts", href: "wins" },
    { label: "Announcements", href: "focus" },
    { label: "Capabilities", href: "roadmap" },
    { label: "Roadmap to 1.0", href: "roadmap-to-1-0" },
    { label: "Proof", href: "proof" },
    { label: "readme.txt", href: "readme" },
  ],
  links: [
    { label: "GitLab", url: "https://gitlab.com/siruiusamory/log1-remake/" },
    { label: "project.json", url: "/project.json" },
  ],
  footerTagline:
    "A toolkit for authoring Legacy of Goku content against the actual LOGII/Buu engine.",
  developmentStatus: "ACTIVE DEVELOPMENT",
  disclaimer:
    "Independent fan development project. Not affiliated with Webfoot Technologies or the relevant game/IP rights holders.",
  assetPolicy:
    "The product captures on this page are unaltered screenshots of the real DragonByte" +
    " Z application, cropped only. They are not mockups, renders or generated images," +
    " and this site ships no generated imagery of any kind.",
};

const buildoutItems = project.buildout.families.flatMap((family) => family.items);

export const buildoutDone = buildoutItems.filter((item) => item.state === "shipped").length;
export const buildoutTotal = buildoutItems.length;
export const buildoutPercent = Math.round((buildoutDone / buildoutTotal) * 100);

const programmeMilestones = project.milestones.filter((m) => m.status !== "target");
export const programmeTotal = programmeMilestones.length;
export const programmeDone = programmeMilestones.filter((m) => m.status === "complete").length;
export const programmePercent = Math.round((programmeDone / programmeTotal) * 100);

export const recentBreakthroughs = project.breakthroughs.filter((b) => b.recent);
export const archivedBreakthroughs = project.breakthroughs.filter((b) => !b.recent);

export const proofStrip = project.metrics.filter((metric) => metric.strip);
export const ledgerMetrics = project.metrics.filter((metric) => !metric.strip);

export const familyTallies = project.buildout.families.map((family) => ({
  key: family.key,
  label: family.label,
  title: family.title,
  done: family.items.filter((item) => item.state === "shipped").length,
  total: family.items.length,
}));

export const roadmapRows = project.buildout.families.flatMap((family) =>
  family.items.map((item) => ({ ...item, family: family.label })),
);

export type RoadmapPhaseState = "complete" | "in-progress" | "next" | "planned";

export interface RoadmapOutcome {
  capabilityId: string;
  title: string;
  detail: string;
}

export interface RoadmapPhase {
  id: string;
  ordinal: string;
  title: string;
  summary: string;
  outcomes: RoadmapOutcome[];
  work: string[];
  state: RoadmapPhaseState;
}

export interface RoadmapTo1 {
  title: string;
  lede: string;
  position: string;
  phases: RoadmapPhase[];
  featureCompleteTitle: string;
  featureComplete: string;
  releaseTitle: string;
  releaseGate: string;
  goldenTitle: string;
  goldenProject: string;
}

const roadmapTo1: RoadmapTo1 = {
  title: "The remaining work, in the order it will happen",
  lede:
    "Every step below is an editor capability a mod author will be able to use,"
    + " not an internal milestone. The count is a count of authoring capabilities,"
    + " so it only moves when the product genuinely gains one.",
  position:
    "The foundation and the authoring-safety baseline are complete, and Phase 2 is"
    + " complete: tile painting, chunk creation, map resizing with layer authoring, and"
    + " warp and connection editing have all shipped. Phase 3, graphics and actor"
    + " authoring, has started with graphics import.",
  phases: [
    {
      id: "foundation",
      ordinal: "0",
      title: "Foundation",
      summary:
        "The groundwork the remaining capabilities build on, already proven"
        + " against a real copy of the game.",
      outcomes: [],
      work: [
        "Editing content that already exists in the game",
        "Building safe derivatives without ever modifying the source file",
        "Authoring proven by running the result in the original engine",
        "ROM expansion to a proven 16 MiB image — expanded space is proven one"
        + " resource family at a time, not for all content at once",
        "A production allocator that places new data and records its provenance",
        "Changing how long an existing line of dialogue is",
        "Map and object authoring foundation",
        "Script and behaviour authoring foundation",
        "Provenance-checked saving, reopening and rebuilding",
      ],
      state: "complete",
    },
    {
      id: "authoring-safety",
      ordinal: "1",
      title: "Authoring safety",
      summary:
        "Make the editor resilient before adding the remaining major creation"
        + " tools, so new surfaces are not built on known state loss or silent"
        + " failures.",
      outcomes: [],
      work: [
        "Preserve unsaved and staged edits when something else changes",
        "Clear, actionable failure messages instead of a dead click",
        "Responsive editing on large projects",
        "Continuous integration that actually exercises the desktop application",
      ],
      state: "complete",
    },
    {
      id: "map-editing",
      ordinal: "2",
      title: "Complete map editing",
      summary:
        "Finish the map editor, building each step on the same view, undo"
        + " history, allocator and safety rules as the last.",
      outcomes: [],
      work: [
        "Tile painting - SHIPPED: pick a chunk a layer already uses and paint"
        + " 256x256 map cells with it, saved through the project and proven on screen"
        + " in the retail engine",
        "Chunk creation - SHIPPED: duplicate a chunk a layer already draws, rearrange"
        + " its 32x32 plane of screen entries using only entries that layer already"
        + " displays, save it as a project-owned chunk with its own identity, place it"
        + " on a map cell, and have the retail engine read the new body from above the"
        + " original ROM's end. Authored chunks are map-scoped",
        "Map resizing and layer authoring - SHIPPED: grow a supported existing map, add"
        + " a supported visual layer, paint the new structure, and have the retail engine"
        + " load the relocated map data. This is growth only - shrinking is not supported",
        "Warps and connections - SHIPPED: retarget an existing transition's destination,"
        + " arrival and facing through the project, or author a transition the image does"
        + " not contain under its own durable identity and build it above the original"
        + " ROM's end. On the map itself, every supported transition is drawn as the"
        + " region that triggers it: a click selects it and a drag moves it as one"
        + " undoable gesture. A human-operated run proved the retail engine consumes an"
        + " authored transition",
      ],
      state: "complete",
    },
    {
      id: "graphics-authoring",
      ordinal: "3",
      title: "Graphics and actor authoring",
      summary:
        "Let an author bring their own art in and build new actors around it,"
        + " with the tool absorbing the format and engine constraints.",
      outcomes: [],
      work: [
        "Graphics import - SHIPPED: edit an extracted sprite asset's PNG in the project," +
        " validate, and build. A re-encoded payload that still fits the slot the original" +
        " occupied is written in place; one that does not is placed by the production" +
        " allocator above the original end of the image, with every confirmed reference to" +
        " it rewritten in the same transaction. A human-operated run proved both halves," +
        " including that the retail engine follows a rewritten reference into expanded" +
        " storage and renders the authored pixels. Same dimensions only - no resizing, no" +
        " new frames - and a confirmed-reference limit that is stated rather than assumed",
        "New sprite, animation and frame authoring - SHIPPED: the Graphics tab's authored" +
        " sprite surface creates the project's one new actor-sprite identity. Choose the" +
        " donor whose proven composition shape every frame keeps, name the sheet each" +
        " animation slot draws from, and choose the existing object slot the appended actor" +
        " starts its behaviour from; the surface refuses a field the build would refuse and" +
        " writes sprites/sprites.toml. A ROM-gated build of that document authors the" +
        " identity and actor the runtime record resolved, and the engine observation covers" +
        " the mechanism: the recorded document carried a neighbouring sibling slot's" +
        " data-pointer word while the surface carries the chosen slot's own, so the" +
        " capability is registered at application proof. Piece and OAM composition, frame" +
        " geometry and frame timing stay outside the modelled contract and the surface says" +
        " so where it is offered",
        "Appearances - SHIPPED: the Graphics tab creates a new appearance definition and" +
        " the build appends it above the image's end, rewriting the five literal words and" +
        " three count bounds that reach the table, with the roster structure built from" +
        " the seen flags relocated alongside it. A driven session watched the retail" +
        " search return an authored record at a post-canonical index, and the Scouter's" +
        " character screen displayed the authored name and description for an actor whose" +
        " retail record reads \"Fighter\". Taking over a retail sprite binding is an" +
        " explicit, default-off choice per definition and the build refuses it otherwise",
      ],
      state: "complete",
    },
    {
      id: "new-map",
      ordinal: "4",
      title: "New map authoring",
      summary:
        "The terminal capability, and deliberately last: it is the point where"
        + " every system above is composed into one new playable area.",
      //: No outcome is promised here any more: an outcome names a capability the
      //: registry still reports missing, and with the denominator complete there
      //: is none. The delivered work is stated in `work` instead.
      outcomes: [],
      work: [
        "New maps - SHIPPED: the Maps editor's New map action records a durable name," +
        " a donor map and the engine's own two-byte key. The build re-emits the whole" +
        " map table above the original end of the image with the authored row appended," +
        " repoints the one literal-pool word the engine's key lookup loads, raises the" +
        " one compiled row bound, and gives the new row its own selector word, its own" +
        " root and its own layer record. A retail map's existing door can then be" +
        " pointed at it. A person-driven session, watched by a read-only observer" +
        " that records the engine's own state, saw the active-MapEntry row become" +
        " index 452 with the authored key, twice, and the player walk in and back" +
        " out. The observer records memory rather than images, so the walking is" +
        " human observation corroborated by the frame-stamped row log",
      ],
      state: "complete",
    },
    {
      id: "creator-experience",
      ordinal: "5",
      title: "Creator experience",
      summary:
        "No new capabilities are added here. This phase makes the 24 that exist"
        + " coherent, recoverable and pleasant to use.",
      outcomes: [],
      work: [
        "Engine limits and resource budgets shown before a build fails",
        "Clear validation and error messages",
        "Consistent undo and redo across every editor",
        "Recovery from interrupted or invalid work",
        "Navigation between related resources",
        "Run and Run From Here workflows",
        "Project and schema migration for older projects",
        "Deterministic reopen and rebuild",
        "Documentation and tutorial polish",
      ],
      state: "planned",
    },
    {
      id: "release",
      ordinal: "6",
      title: "DragonByte Z 1.0",
      summary:
        "The release gate. A feature-complete product still has to be"
        + " installable, documented, distributable and verified on real hardware.",
      outcomes: [],
      work: [
        "Packaged Windows release",
        "Clean first-run and setup",
        "Supported-ROM verification",
        "Safe build and provenance",
        "Distributable patch output",
        "Complete guide and tutorial",
        "Emulator validation",
        "Real-hardware and flashcart smoke test",
        "Final end-to-end authored project",
      ],
      state: "planned",
    },
  ],
  featureCompleteTitle: "100% is not the same milestone as 1.0",
  featureComplete:
    "Reaching 24 of 24 means every planned authoring capability exists. Before"
    + " the tool can be called 1.0, the remaining work is polish, reliability,"
    + " packaging, documentation and release validation — so a complete feature"
    + " list is not an automatic release.",
  releaseTitle: "The 1.0 release gate",
  releaseGate:
    "Nothing in the release phase adds an authoring capability. It makes the"
    + " finished tool something a normal person can install, learn, trust and"
    + " distribute.",
  goldenTitle: "The final acceptance project",
  goldenProject:
    "Before 1.0, DragonByte Z must be able to create a completely new playable"
    + " area — from map art and graphics through NPCs, behaviour and dialogue —"
    + " build it into the real Buu's Fury engine, reopen the project, modify it"
    + " again and produce a distributable patch, without a hex editor or any"
    + " manually entered ROM offset.",
};

export interface RoadmapPhaseView extends RoadmapPhase {
  done: number;
  outcomeTotals: number[];
}

function accumulateRoadmap(base: number): RoadmapPhaseView[] {
  let running = base;
  return roadmapTo1.phases.map((phase) => {
    const outcomeTotals = phase.outcomes.map((_outcome) => (running += 1));
    return { ...phase, done: running, outcomeTotals };
  });
}

export const roadmapBase = buildoutDone;
export const roadmapPhases = accumulateRoadmap(roadmapBase);
export const roadmap = { ...roadmapTo1, phases: roadmapPhases };

export const roadmapNextPhase = roadmapPhases.find((phase) => phase.state === "next");

export const roadmapActivePhase = roadmapPhases.find((phase) => phase.state === "in-progress");

export const roadmapStateLabel: Record<RoadmapPhaseState, string> = {
  complete: "COMPLETE",
  "in-progress": "IN PROGRESS",
  next: "NEXT — NOT STARTED",
  planned: "PLANNED",
};

const SHIPPED_MARKER = " - SHIPPED: ";

export function roadmapWorkItem(text: string): { name: string; detail?: string; shipped: boolean } {
  const [name, detail] = text.split(SHIPPED_MARKER);
  return { name, detail, shipped: detail !== undefined };
}

function validateRoadmapTo1(): void {
  const promised = roadmapTo1.phases.flatMap((phase) =>
    phase.outcomes.map((outcome) => outcome.capabilityId),
  );

  const duplicate = promised.find((id, index) => promised.indexOf(id) !== index);
  if (duplicate) {
    throw new Error(`The roadmap to 1.0 ships capability "${duplicate}" more than once.`);
  }

  const outstanding = registry.capabilities
    .filter((capability) => capability.state !== "shipped")
    .map((capability) => capability.id);
  const unknown = promised.filter((id) => !outstanding.includes(id));
  if (unknown.length) {
    throw new Error(
      `The roadmap to 1.0 ships ${unknown.join(", ")}, which the registry does not report as missing.`,
    );
  }
  const unplanned = outstanding.filter((id) => !promised.includes(id));
  if (unplanned.length) {
    throw new Error(
      `The registry reports ${unplanned.join(", ")} missing, but the roadmap to 1.0 never ships it.`,
    );
  }

  const order: RoadmapPhaseState[] = roadmapTo1.phases.map((phase) => phase.state);
  const rank: Record<RoadmapPhaseState, number> = {
    complete: 0,
    "in-progress": 1,
    next: 2,
    planned: 3,
  };
  for (let index = 1; index < order.length; index += 1) {
    if (rank[order[index]] < rank[order[index - 1]]) {
      throw new Error("The roadmap to 1.0 lists a phase out of order.");
    }
  }

  const nextCount = order.filter((state) => state === "next").length;
  if (nextCount > 1) {
    throw new Error("The roadmap to 1.0 names more than one next phase.");
  }

  for (const phase of roadmapTo1.phases) {
    if (!phase.title.trim() || !phase.summary.trim()) {
      throw new Error(`Roadmap phase "${phase.id}" is missing its title or summary.`);
    }
    if (!phase.outcomes.length && !phase.work.length) {
      throw new Error(`Roadmap phase "${phase.id}" describes no work at all.`);
    }
    for (const item of phase.work) {
      if (/\bshipped\s*:/i.test(item) && !roadmapWorkItem(item).shipped) {
        throw new Error(
          `Roadmap phase "${phase.id}" marks work as shipped without the "${SHIPPED_MARKER.trim()}" separator: "${item.slice(0, 40)}".`,
        );
      }
    }
  }

  const finalDone = roadmapPhases[roadmapPhases.length - 1].done;
  if (finalDone !== buildoutTotal) {
    throw new Error(
      `The roadmap to 1.0 finishes at ${finalDone} of ${buildoutTotal}; the phases must reach the whole denominator.`,
    );
  }
}

validateRoadmapTo1();

function groupMetrics(metrics: ProjectMetric[]): { group: string; metrics: ProjectMetric[] }[] {
  return metrics.reduce(
    (groups, metric) => {
      const existing = groups.find((g) => g.group === metric.group);
      if (existing) existing.metrics.push(metric);
      else groups.push({ group: metric.group, metrics: [metric] });
      return groups;
    },
    [] as { group: string; metrics: ProjectMetric[] }[],
  );
}

export const ledgerGroups = groupMetrics(ledgerMetrics);

function validateProjectStatus(value: ProjectStatus): void {
  if (!value.blockerTitle.trim()) {
    throw new Error("Project status must include a current blocker title.");
  }

  if (!value.acceptanceTarget.trim() || !value.milestones.some(({ status }) => status === "target")) {
    throw new Error("Project status must include an acceptance target and a target milestone.");
  }

  const currentMilestones = value.milestones.filter(({ status }) => status === "current");
  if (currentMilestones.length !== 0) {
    throw new Error(
      `The completed authoring programme may not contain a current milestone; found ${currentMilestones.length}.`,
    );
  }

  const keys = buildoutItems.map((item) => item.key);
  const duplicate = keys.find((key, index) => keys.indexOf(key) !== index);
  if (duplicate) {
    throw new Error(`Buildout capability keys must be unique; "${duplicate}" appears twice.`);
  }

  //: A complete buildout is a legitimate state - `docs/ROADMAP_TO_1_0.md` calls
  //: 24/24 feature complete - so this guard refuses an EMPTY buildout rather than
  //: requiring a missing capability. The percent bound below still holds at 100.
  if (!buildoutTotal || !buildoutDone) {
    throw new Error("The buildout must report at least one shipped capability.");
  }

  if (buildoutPercent < 0 || buildoutPercent > 100) {
    throw new Error("Derived buildout progress must fall between 0 and 100.");
  }

  if (!value.figures.length || value.figures.some(({ src }) => !src.trim())) {
    throw new Error("Project status must include the real product captures it ships.");
  }

  if (!value.assetPolicy.trim()) {
    throw new Error("Project status must state its shipped-asset policy.");
  }
}

validateProjectStatus(project);

export const statusMeta: Record<MilestoneStatus, { label: string }> = {
  complete: { label: "COMPLETE" },
  current: { label: "CURRENT" },
  next: { label: "NEXT" },
  target: { label: "TARGET" },
};
