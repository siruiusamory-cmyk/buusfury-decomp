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
    "The broad engine-archaeology phase is complete and that research queue is closed." +
    " The SDK extracts a complete resource library from the user's own copy of the game" +
    " and curates it into a clean, human-browsable resource pack with ROM-derived names" +
    " and a full source map. DragonByte Z renders retail maps directly from immutable" +
    " ROM data and supports direct visual placement editing on the actual game map, and" +
    " the editor now grows one feature at a time against the curated corpus.",
  overallProgress: 97,
  overallProgressLabel: "≈ 97% COMPLETE",
  progressCaveat:
    "Progress is a directional project estimate. The milestones below are the authoritative measure of capability.",
  currentPhase: "DRAGONBYTE Z BUILDOUT",
  currentFrontierLabel: "CURRENT FRONTIER",
  existingContentState: "MATURE",
  blockerCode: "DRAGONBYTE Z FEATURES",
  blockerTitle: "Build DragonByte Z out feature by feature",
  blockerShort:
    "The resource pipeline is complete and curated: the SDK extracts every known map" +
    " layer, tile, chunk, sprite, animation and frame from the user's own ROM, and a" +
    " second pass organises that corpus into a clean, human-browsable resource pack" +
    " with ROM-derived names and a complete source map. The next step is growing the" +
    " desktop editor one feature at a time against that corpus - browsing and viewing," +
    " then editing - instead of waiting for full arbitrary-content authoring to be" +
    " solved first.",
  blockerParagraphs: [
    "The resource pipeline is finished. The exporter walks the game's own structures -" +
    " 452 maps, every map-layer reference classified, complete tile, chunk, sprite," +
    " animation, frame and graphics populations - and the curator turns that raw output" +
    " into a clean, human-navigable library: ROM-derived and neutral names, no generated" +
    " prose, a deterministic rebuild, and a complete curated-to-raw source map. The" +
    " canonical raw library stays byte-for-byte untouched.",
    "What remains is building the desktop editor, not re-extracting the game. DragonByte" +
    " Z already renders retail maps and supports direct visual placement editing. A" +
    " fixed-size map-layout pointer edit is now a usable feature there: pick a 256x256" +
    " chunk cell, swap in another chunk the same layer already uses, preview it, and" +
    " save a new ROM. The editor grows one feature at a time - browsing and viewing," +
    " then editing surfaces such as this one, then tiles, sprites, animations and" +
    " frames, and later warp editing and graphics replacement.",
    "Authoring entirely new content remains the project's final acceptance target and is" +
    " no longer the organising priority for current tool work. The overall estimate stays" +
    " at 97%.",
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
        "A message can be any length in storage, and a long line runs past the edges of the screen when the game draws it centred without wrapping.",
      technical:
        "Measured. Storage length no longer bounds an authored message; the remaining limit on this particular message style is display width, because the engine draws it centred in a large font with no wrapping. The character ceiling and the cost of adding line breaks are not yet measured. This is a known constraint of one message style rather than the project's frontier.",
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
      id: "graphical-workbench",
      title: "Drive the SDK from a desktop tool",
      plainEnglish:
        "Do the whole find, inspect, build and run loop from a graphical application instead of the command line.",
      technical:
        "Confirmed. The Webfoot Workbench is a desktop GUI and a second client of the same SDK, with four tabs backing the full loop: search the atlas, inspect an object or text record, build the game, and run the build. The build panel refuses to write over the source ROM. Graphical dialogue editing is intentionally not part of this milestone.",
      status: "complete",
    },
    {
      id: "gui-dialogue-editing",
      title: "Edit dialogue inside the Workbench",
      plainEnglish:
        "Search a supported line in the desktop tool, edit it, then build and run it — all without touching the command line.",
      technical:
        "Confirmed. The Inspector resolves mapped semantic targets through the production authoring API, keeps original, saved and unsaved values distinct, validates before mutation, persists the normal project schema, invalidates stale validation/build state, and builds through validate_project and build_project. The goku-greeting workflow was completed twice through the GUI and the retail engine displayed Nice work, Goku!; unsupported search results remain read-only.",
      status: "complete",
    },
    {
      id: "playable-scene-authoring",
      title: "Author a complete playable scene in Workbench",
      plainEnglish:
        "Bring entity, placement, script, and dialogue authoring together in the desktop tool so a whole playable scene can be built without hand-operating the SDK.",
      technical:
        "Confirmed and runtime-proven. The owner personally authored a complete playable NPC scene entirely through the Workbench GUI: select map:0040, clone a type_0086 enemy-linked placement, configure the entity, assign an on_defeat behavior plus an authored show_centered_sprite_text script, then Validate, Build, and Launch. Defeating the NPC in the retail Buu's Fury engine displayed the authored banner in-game. No new reverse engineering was required; every capability was surfaced through the existing SDK. Independent review approved.",
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
        "Delivered. The multi-map semantic workspace keeps a scene's relationships together and reviews pending changes in author-facing language, and authoring moved from list-and-form interaction toward direct visual selection, which is the real answer to the friction the owner reported.",
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
        "See the game's actual sprites, frames, animations, and palettes, select them by sight, edit a colour, and watch the change appear in the running game.",
      technical:
        "Sprite browsing and palette editing are runtime-proven. DragonByte Z renders supported retail maps through the SDK's ROM-only renderer and overlays neutral placement markers at the proven signed map-pixel coordinates. The owner used the map itself to select, add, and move an object, then built and confirmed the generated ROM in the retail Buu's Fury engine. The GUI stays a thin client over semantic scene and project APIs; it contains no map-format or direct-ROM-write logic.",
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
        "The exporter output is complete and deterministic, but it is not yet organised:" +
        " the work is measuring and reducing redundancy and improving navigation while" +
        " proving that every structural fact the exporter recorded still resolves. No" +
        " extraction, classification or rendering behaviour changes.",
      status: "complete",
    },
    {
      id: "dragonbyte-z-buildout",
      title: "Build DragonByte Z out feature by feature",
      plainEnglish:
        "Grow the desktop editor one feature at a time against the verified resource" +
        " corpus instead of waiting for everything to be solved first.",
      technical:
        "The map canvas itself is already proven: DragonByte Z renders supported retail" +
        " maps from ROM and lets an author select, add and move objects directly on them." +
        " Map Browser's Edit Layout mode now turns a fixed-size chunk-pointer" +
        " replacement into a usable feature: it draws a map's 256x256 chunk cells," +
        " offers only chunks that same layer already uses, previews the swap" +
        " immediately, and saves the pending edits to a new ROM. 341 of the 452 maps" +
        " expose an editable layer and the rest stay read-only, and the source game" +
        " file is never modified. Tile painting, new chunks, resizing, warp editing" +
        " and graphics replacement remain future work. This is a direction rather" +
        " than a committed engineering order.",
      status: "current",
    },
    {
      id: "playable-log1",
      title: "Playable LOG1 content in the real engine",
      plainEnglish: "Build and play newly authored Legacy of Goku content using the original Webfoot game engine.",
      technical:
        "This is the mandatory acceptance target for Webfoot SDK. Authoring entirely new" +
        " content remains the goal; it is simply no longer the organising priority for" +
        " current tool development.",
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
    { label: "DRAGONBYTE Z FEATURES", state: "current", marker: "↑ YOU ARE HERE" },
    { label: "ADVANCED AUTHORING / AUTHOR_NEW", state: "target" },
    { label: "PLAYABLE LOG1 CONTENT", state: "target" },
  ],
  breakthroughs: [
    {
      id: "fixed-size-map-layout-write",
      title: "First reversible map-layout write",
      summary:
        "A retail map's layout can now be edited from DragonByte Z: swap one chunk cell" +
        " for another chunk the same layer already uses, preview it, and save a new" +
        " game file that re-renders with the change.",
      technical:
        "On Buu's Fury map:0040, dominant layer 1 cell 0 was redirected to another" +
        " chunk already used by that layer. Exactly two ROM bytes changed within its" +
        " four-byte pointer; the changed 256-by-256-pixel region re-rendered through" +
        " the accepted map pipeline. No-op and inverse builds matched all 8,388,608" +
        " canonical bytes. The source ROM was not modified. DragonByte Z's Map Browser" +
        " now drives exactly this operation in its Edit Layout mode, over 341 of the" +
        " 452 maps. This proves only fixed-size in-place layout replacement; emulator" +
        " validation was not performed.",
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
        " structured graphics containers.",
    },
    {
      id: "research-freeze-complete",
      title: "Engine archaeology and final synthesis complete",
      summary:
        "The broad reverse-engineering programme that underpinned the toolkit is finished," +
        " and its results are consolidated into canonical schemas.",
      technical:
        "The ten-ticket archaeology queue and its consolidation close out, each read through" +
        " its own accepted review, closeout and provenance record. Further work is targeted" +
        " and capability-driven rather than a new archaeology queue.",
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
        "Runtime-proven on map:0041 after the earlier map:0040 scene. The owner selected the map, cloned and configured a supported entity, assigned behavior and a visible response, reviewed project changes, validated, built, launched, reached the map, and observed the authored interaction—without raw ROM addresses or project-file editing. Independent review approved the thin-client architecture.",
    },
    {
      id: "scene-authored-through-workbench",
      title: "First complete playable scene authored entirely in the desktop tool",
      summary:
        "The project owner built a full playable NPC scene from start to finish inside Webfoot Workbench — choosing a map, placing an enemy, giving it behavior, a script, a defeat trigger, and an author-written message, then validating, building, and launching — with no Python, TOML, command line, or hex. Defeating the NPC in the original Buu's Fury engine showed the authored banner on screen.",
      technical:
        "Runtime-proven and independently approved. The scene was authored on map:0040: clone a type_0086 enemy-linked placement, configure the entity, assign an on_defeat behavior plus an authored show_centered_sprite_text script, then Validate, Build, Launch, defeat the NPC, and observe the authored banner in the retail engine — every step through the GUI. No new reverse engineering was required; the capabilities were surfaced through the existing SDK. The proven scene is deliberately one authored record plus one line of text, which makes breadth the next frontier.",
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
        "A standalone reference covering what the project has established about the Buu's Fury game data, written for other people working on the same game and shared with the Legacy of Goku community on their Discord server. It is a document shared there, not a page hosted on this site.",
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
    { label: "Maps extracted", value: "452" },
    { label: "Map layer references classified", value: "1,808 / 1,808" },
    { label: "Graphical map layers exported", value: "1,559" },
    { label: "Unresolved graphical layers", value: "0" },
    { label: "Tile banks extracted", value: "187" },
    { label: "Individual tiles extracted", value: "47,857" },
    { label: "Map chunks extracted", value: "3,745" },
    { label: "Sprite definitions extracted", value: "297" },
    { label: "Animation slots extracted", value: "4,070" },
    { label: "Frame records extracted", value: "10,980" },
    { label: "Sprite pieces extracted", value: "11,005" },
    { label: "Structured sprite graphics extracted", value: "7,390" },
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
