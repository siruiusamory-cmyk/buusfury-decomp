param(
    [Parameter(Mandatory = $true)]
    [int]$TargetProcessId,
    [Parameter(Mandatory = $true)]
    [string]$LuaPath,
    [string]$ReadyPath,
    [string]$MarkerPath,
    # A Lua statement run immediately AFTER the observer's dofile and before the
    # ready marker. The mgba-runtime skill's proven ordering is "inject the
    # observer, then load the savestate": entities are built during a state load,
    # so a breakpoint armed afterwards never sees construction. This is where the
    # state load therefore goes. It is a separate parameter rather than a line in
    # the observer because an observer stays read-only and a state load is not.
    [string]$PostCommand,
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$allowedLua = @(
    # Added by DIALOGUE-RENDER-PATH-001 and published with the dialogue research
    # set: the dialogue strip observer. READ-ONLY. It arms five breakpoints - the
    # glyph composer at 0x0803DE5E, the persistent-cursor store at 0x0800B08E, the
    # source-consume store at 0x0800B092, the reveal queue store at 0x0800B006 and
    # the dialogue record copier at 0x0801227A - dumps the 128-entry OAM per
    # snapshot and byte-diffs the OBJ VRAM window 0x06014360..0x06014EC0. It writes
    # no emulated memory and presses no keys; it writes host files inside the run
    # directory only.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\dialogue_strip_probe.lua')
    )
    # Added by DIALOGUE-TOKEN-PRODUCTIZATION-001: the token-lookup observer. The
    # strip probe logs composition and advance but never the SOURCE UNIT handed to
    # the token lookup, which is the one value that tells whether the line fitter
    # and the composer agree about a unit. This one arms the lookup, the fitter's
    # token branch, the shared glyph advance, the cave's expansion loop, the game's
    # composer and the record copier as liveness, and reads registers only. It
    # writes no emulated memory, presses no keys and writes host files inside the
    # run directory only.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\dialogue_token_probe.lua')
    )
    # Added by FRIEND-V3-COLD-BOOT-ACCEPTANCE-001: the cold-boot acceptance
    # observer. Every earlier Kibito comparison loaded a savestate whose EWRAM
    # held dialogue decoded on an older build, so each compared the image beside
    # restored RAM. This one is for a launch with no savestate: it logs the
    # engine's own record copies with a text snippet from each pointer register,
    # counts the dialogue copier as a liveness channel, and screenshots every
    # five seconds. It reads registers and memory only, arms one breakpoint,
    # writes host files inside the run directory, and never touches input.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\friendv3_coldboot_probe.lua')
    )
    # Added by DIALOGUE-RENDER-PATH-001 and published with the dialogue research
    # set: the dialogue input driver. It is DRIVING CODE in its own file, which is
    # why it is separate from the observer above. It presses A once every 180
    # frames for six frames and nothing else - no directional input, no mashing,
    # because a direction walks the character off the NPC and mashing skips the
    # per-glyph reveal being measured. It touches no emulated memory and writes no
    # file.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\npc_talk_driver.lua')
    )
    # Added by APPEARANCE-AUTHORING-GATE-001: the appearance-table observer. It
    # writes no emulated memory and arms fifteen sites - the six reader functions'
    # entry points,
    # the six literal-pool base-load sites inside them, the search loop's record
    # read, the roster walk's patched bound and the animation frame advance - and
    # writes only host files inside the run directory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\appearance001_table_watch.lua')
    )
    # Added by APPEARANCE-ROSTER-EXPANSION-001: the roster-object observer. It
    # writes no emulated memory. It samples the context word at 0x03000F90 for the
    # list object the engine builds from the seen-flag array, reads the seen flag
    # for the authored index and both display-count offsets, and presses Select
    # (the game's Scouter button) and Start, bounded by its own schedule.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\roster001_scouter_watch.lua')
    )
    # Added by MAP-WARP-RUNTIME-EDIT-001: the read-only transition observer. It
    # reads the live map identity each frame plus the target record's destination
    # key through the engine's own MapEntry+0x2C -> root+0x44 route, and writes
    # only host files inside the run directory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\warpedit001_transition_watch.lua')
    )
    # Added by MAP-NEW-AUTHORING-001: the live map-identity observer. It writes no
    # emulated memory and presses no keys. It derives the loaded map row from the
    # engine's own active-MapEntry pointer 0x03001980, the table base from the
    # literal pool word the engine's key lookup loads at 0x08008A58, and the row
    # bound from the count helper at 0x080125E0, then reads that row's key bytes,
    # its +0x2C source word and the root it names - so a map identity the
    # canonical image does not contain is reported as the row the engine loaded
    # rather than asserted. It writes only host files inside the run directory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapnew001_live_identity.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom007_move_south.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom009_clean_route.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom009_post_transition_route.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom011_human_ready.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom011_stop_setup.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom011_idle_benchmark.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p002_walk_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_attack_scout.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_move_attack.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_punch_timing.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_hit_dump.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_hit_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_wander.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_watcher.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_mash.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_armed_punch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_armed_mash.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_armed_one.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_human_play.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_zdump.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_human_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_punch_label.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_full_label.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_fine.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_actor_focus.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_aggro.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_reaction_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_anchor_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_dev_breakpoint_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_ctrl_stack.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_scan_timing_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_ctrl_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_pool_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_punch_field_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p007_wolf_ai_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p008_clip_sequence.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p008_mash_driver.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p008_contact_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p010_death_timeline.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_hit_bracket_scan.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit029_placement_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit030_behavior_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit031_api_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit031_execution_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit034_dispatch_caller_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit032_authored_script_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit033_gameplay_effect_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit036_text_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit037_dialogue_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom_expand_001_dialogue_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom_expand_001_dialogue_driver.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom_expand_001_snapshot.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\capacity001_expanded_dialogue_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit038_scenario_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\text_handle_001_producer_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\text_handle_002_handler_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapvis001_vram_dump.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapvis001_vram_dump_any.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapvis002_bg_provenance.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\placementpos001_construct_watch.lua')
    )
    # Added by ASSET-EXPORT-MAP19-001: read-only BG/VRAM placement observer
    # for the terrain-field layer. It reads registers and VRAM and writes
    # only host text.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\map19_bg_placement.lua')
    )
    # Added by DIALOGUE-VARIABLE-LENGTH-001: the same read-only consumer
    # observation and screenshot schedule as the Checkpoint D probe, retargeted
    # at a RE-AUTHORED handle and widened decoded length. It writes input only in
    # its `scripted` mode, which the tracked runner does not select, and never
    # writes emulated memory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\varlen001_dialogue_variable_length_probe.lua')
    )
    # Added by MAP-TILE-PAINT-001: the read-only live-screenblock observer. It
    # reads emulated memory and its own latched registers and writes host files
    # under the run directory; it contains none of the input- or memory-writing
    # API names the read-only guard in tests/unit/test_mgba_capture.py greps for,
    # so the observer guarantee holds, and that test names this file explicitly.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\tilepaint001_live_screenblock.lua')
    )
    # The leave-and-re-enter watcher: same read-only guarantees, but it latches a
    # numbered snapshot whenever the engine's screenblock content changes, which
    # is how an area rebuild is captured without timing a keypress.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\tilepaint001_watch_rebuild.lua')
    )
    # The same watcher for MAP-CHUNK-AUTHORING-001. It additionally accepts the
    # profile's generated 16 MiB image size - the authored chunk body lives above
    # the canonical EOF, so the parent observer's 8 MiB assert refuses the image
    # under test - records the observed ROM size on every row, and records the
    # address the engine's own loaded layer record holds for the watched chunk
    # cell. Read-only in exactly the same sense.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\chunkauth001_watch_rebuild.lua')
    )
    # Added by MAP-GFX-DIAG-001: the read-only assembled-background observer. It
    # dumps the engine's own VRAM, palette and IO once a target map has been
    # departed and re-entered, and records the root, layer records and extent the
    # LIVE image holds. Read-only in exactly the same sense as the observers
    # above; tests/unit/test_mgba_capture.py names this file explicitly.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapgfxdiag001_map_layer_dump.lua')
    )
    # Added by ROMHACK-WARP-RANDOMIZER-001: the read-only map-arrival observer for
    # the human-operated randomized playthrough. It latches the live map identity
    # on every map change, and the identity it came from, so each naturally
    # encountered warp has a source and a destination that came out of the
    # running engine rather than a map-name guess. It reads emulated memory and
    # writes only host files inside the run directory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\warprand001_map_watch.lua')
    )
    # Added by MAP-WARP-CREATE-RUNTIME-001: the read-only observer for a CREATED
    # transition. Where the warp observers above follow an array element that
    # already existed, this one follows the element the build APPENDED (index 2 on
    # map 40) and records the whole engine route to it, so the run proves the
    # engine reached the NEW element and the NEW record rather than a record that
    # was already there. It reads emulated memory and writes only host files inside
    # the run directory, and it accepts both the canonical 8 MiB image and the
    # 16 MiB derivative that carries the new structure above the original EOF.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\warpcreate001_transition_watch.lua')
    )
    # Added by GRAPHICS-IMPORT-BOUNDARY-001: the read-only observer for a
    # human-played proof that the retail engine renders AUTHORED actor-sprite
    # pixels, including a re-encoded payload the allocator placed above canonical
    # EOF. It captures every screen whose object-tile region has settled, with
    # the live map index, so the analysis afterwards chooses the gameplay frame
    # from the sequence instead of the instrument guessing it. It reads emulated
    # memory and writes only host files inside the run directory, and it accepts
    # both the canonical 8 MiB image and the 16 MiB generated one.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\gfximport001_pixel_proof.lua')
    )
    # Added by RANDOMIZER-ENEMY-PACK-001: the read-only map-identity and liveness
    # observer for the randomized-enemy smoke. It latches the engine's live
    # MapEntry pointer and the map index it resolves to, emits a heartbeat on a
    # fixed frame stride so an empty log can never be read as a negative, and
    # takes host-side screenshots. It writes no emulated memory and drives no
    # input; tests/unit/test_mgba_capture.py names this file explicitly.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\enemypack001_observer.lua')
    )
    # Added by RANDOMIZER-ENEMY-PACK-001: the live placement-slot enumerator. It
    # walks the engine's own map object array (MapEntry+0x04 count, +0x14 array)
    # and reads each placement record's stat selector (+0x08) and sprite id
    # (+0x10) out of the ROM the engine is actually running, so the same
    # savestate can be compared across the canonical and a randomized image. It
    # calls emu:read8/read32 and emu:screenshot only; tests/unit/test_mgba_capture.py
    # names this file explicitly.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\enemypack002_live_slots.lua')
    )
    # Added by SPRITE-NEW-RUNTIME-001: the read-only new-identity observer. It
    # installs one breakpoint at 0x0800F6B4, the instruction after the registry
    # accessor returns inside the placement constructor, and records the
    # placement, the sprite id it asked for, the actor being built and the
    # character structure the engine resolved, so a hit on the new identity's
    # address is the engine's own statement that it resolved an identity the
    # retail image does not contain. It reads memory, screenshots, and taps a
    # controller key only on a named schedule; it writes no emulated memory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\spritenew001_observer.lua')
    )
    # Added by SPRITE-NEW-RECORD-RUN-001: the read-only object-run observer. It
    # records the three ends of the sibling-family dispatch - the map object loop
    # where the array names a record, the factory where the engine resolves that
    # record's sprite id, and the behaviour constructor where the pointer the
    # engine passes does not equal the record the array named - plus a per-word
    # movement window over every behaviour object it sees. It reads memory and
    # screenshots, and taps a controller key only on the named `menu` schedule
    # that loads the saved game; it writes no emulated memory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\spritenew002_record_run.lua')
    )
    # Added by SPRITE-NEW-RECORD-RUN-001: the two-breakpoint dispatch-table probe.
    # The main observer above arms six breakpoints and the one on the dispatcher
    # never reported a hit there in any registration order while the other five
    # all produced data, so this probe arms that site and one liveness control and
    # nothing else. "No hit" then means the site was not executed rather than that
    # the breakpoint could not be installed. It is strictly read-only - it reads
    # memory and registers and writes host files only, and drives no input at all,
    # because the run it exists for loads a savestate from the launcher instead.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\spritenew003_dispatch_probe.lua')
    )
    # Added by SPRITE-NEW-BEHAVIOR-REGISTRATION-001: the read-only registration
    # observer. It records the block installer 0x0800A93C (which is what writes
    # the table pointer into actor+0x1B0+0x08), both behaviour-constructor classes
    # the dispatcher calls (0x0800A7A0 and 0x0800A222), the class-A behaviour
    # object, the dispatcher's own table-entry site 0x0800A9A4 re-armed as a
    # contradiction check, the map-102 record factory, and a per-word movement
    # window over every actor the dispatch reached. It reads memory and registers,
    # screenshots, and taps a controller key only on the named `menu` schedule that
    # loads the saved game; it writes no emulated memory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\spritenew004_registration.lua')
    ),
    # Added by SPRITE-NEW-RUNTIME-PARITY-001: the read-only parity observer.
    # It records the map object factory's resolution site 0x08017DB0, the walk
    # action's result and step direction at 0x0800A3B0, and a periodic sample of
    # every actor that reached the walk action: world position (+0x1A0/+0x1A4)
    # and the frame record it is drawing (+0x54), which maps to the authored
    # cell and therefore to the facing. It reads memory and registers,
    # screenshots, and taps a controller key only on the named `menu` schedule
    # that loads the saved game; it writes no emulated memory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\spritenew005_parity.lua')
    ),
    # Added by RUNTIME-LUA-INJECTOR-CONSOLIDATION-001: the two ROM-006 bootstrap
    # scripts, moved here from the private allowlist load_mgba_lua.ps1 used to carry
    # so that membership is decided in exactly one place. Both drive input
    # (emu:setKeys, emu:addKey, emu:clearKey), write one savestate
    # (emu:saveStateFile) and take one screenshot, which is what makes the two
    # ROM-006 samples deterministic. Both reset the core, pulse A on named frames
    # and self-terminate, they write only beneath build\rom006, and each opens with
    # assert(emu:getGameCode() == "AGB-BG3E"), so they are only valid on the 0.10.5
    # build that load_mgba_lua.ps1 pins by VersionInfo.FileVersion. The ROM-006 GDB
    # sample that consumes the state is tools/runtime/rom006_gdb_probe.py.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom006_bootstrap.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom006_bootstrap_map4.lua')
    )
    # Added by FRIEND-V3-TULMA-GRAPHICS-001: the read-only settled-screen observer
    # for the Tulma session. It samples the object-tile region every frame for a
    # still signature, and on a settle writes a screenshot plus full VRAM, palette
    # and OAM dumps into the run directory, so whether the engine drew the authored
    # tiles is measured against the dumped object-tile bytes rather than judged from
    # a picture. It presses no key and writes no emulated memory. It accepts only the
    # image sizes this ticket owns, which it names in its own header; a size outside
    # that list throws on load and the launcher then reports the misleading "Lua
    # script did not report ready", so the two are updated together.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\tulma001_tulma_proof.lua')
    )
)
$resolvedLua = [System.IO.Path]::GetFullPath($LuaPath)
if ($resolvedLua -notin $allowedLua) {
    throw 'LuaPath is not an allowlisted tracked movement script'
}
$resolvedReady = $null
if ($ReadyPath) {
    $resolvedReady = [System.IO.Path]::GetFullPath($ReadyPath)
    $allowedReadyRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'build')
    ).TrimEnd('\') + '\'
    if (-not $resolvedReady.StartsWith(
        $allowedReadyRoot,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'ReadyPath must remain beneath ignored build directory'
    }
    if ($resolvedReady.Contains(']]')) {
        throw 'ReadyPath contains unsupported Lua long-string terminator'
    }
    if (Test-Path -LiteralPath $resolvedReady) {
        throw 'ReadyPath already exists'
    }
}
$resolvedMarker = $null
if ($MarkerPath) {
    $resolvedMarker = [System.IO.Path]::GetFullPath($MarkerPath)
    $allowedMarkerRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'build')
    ).TrimEnd('\') + '\'
    if (-not $resolvedMarker.StartsWith(
        $allowedMarkerRoot,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'MarkerPath must remain beneath ignored build directory'
    }
    if ($resolvedMarker.Contains(']]')) {
        throw 'MarkerPath contains unsupported Lua long-string terminator'
    }
    if (Test-Path -LiteralPath $resolvedMarker) {
        throw 'MarkerPath already exists'
    }
}


if ($CheckOnly) {
    # A launcher that hands mGBA --script at startup still needs the allowlist
    # and the path rules to be the gate, so it asks this script to do every check
    # and stops here, before any window is touched.
    Write-Output $resolvedLua
    exit 0
}

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$processCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $TargetProcessId
)
$scriptingCondition = New-Object System.Windows.Automation.AndCondition(
    $processCondition,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Scripting'
    ))
)
$scripting = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $scriptingCondition
)

$mainWindow = $null
for ($attempt = 0; $attempt -lt 200 -and -not $mainWindow; $attempt++) {
    Start-Sleep -Milliseconds 100
    $windows = $desktop.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        $processCondition
    )
    foreach ($window in $windows) {
        if ($window.Current.Name -match "Buu's Fury|DBZBUUSFURY") {
            $mainWindow = $window
            break
        }
    }
}
if (-not $mainWindow) {
    throw 'mGBA did not report the loaded Buu''s Fury ROM title'
}

if (-not $scripting) {
    $tools = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty,
            'Tools'
        ))
    )
    if (-not $tools) {
        $allNames = @()
        foreach ($el in $mainWindow.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                [System.Windows.Automation.Condition]::TrueCondition)) {
            $allNames += $el.Current.Name
        }
        Write-Output ("UIA tree: " + ($allNames -join ' | '))
        throw 'Tools menu not found'
    }
    $tools.GetCurrentPattern(
        [System.Windows.Automation.ExpandCollapsePattern]::Pattern
    ).Expand()

    $scriptCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Scripting...'
    )
    $scriptMenu = $null
    for ($attempt = 0; $attempt -lt 50 -and -not $scriptMenu; $attempt++) {
        Start-Sleep -Milliseconds 100
        $scriptMenu = $desktop.FindFirst(
            [System.Windows.Automation.TreeScope]::Descendants,
            $scriptCondition
        )
    }
    if (-not $scriptMenu) { throw 'Scripting menu item not found' }
    $scriptMenu.GetCurrentPattern(
        [System.Windows.Automation.InvokePattern]::Pattern
    ).Invoke()

    for ($attempt = 0; $attempt -lt 50 -and -not $scripting; $attempt++) {
        Start-Sleep -Milliseconds 100
        $scripting = $desktop.FindFirst(
            [System.Windows.Automation.TreeScope]::Children,
            $scriptingCondition
        )
    }
    if (-not $scripting) { throw 'Scripting window did not appear' }
}

$edits = $scripting.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    ))
)
# Identify the prompt by control identity, not by IsReadOnly. The Scripting
# window exposes three Edit elements - the log pane, the script buffer, and the
# prompt - and Qt does not always report IsReadOnly for them. When that property
# comes back empty, "-not IsReadOnly" is true for the log pane, which is the
# first descendant, so SetValue then fails with "Value is read-only."
$prompt = $null
foreach ($edit in $edits) {
    $automationId = $edit.Current.AutomationId
    if ($automationId -and $automationId.EndsWith('.prompt')) {
        $prompt = $edit
        break
    }
}
if (-not $prompt) {
    foreach ($edit in $edits) {
        if ($edit.Current.ClassName -eq 'QGBA::HistoryLineEdit') {
            $prompt = $edit
            break
        }
    }
}
if (-not $prompt) {
    foreach ($edit in $edits) {
        if ($edit.Current.IsReadOnly -eq $false) { $prompt = $edit; break }
    }
}
if (-not $prompt) { throw 'Scripting prompt not found' }
$command = ''
if ($resolvedMarker) {
    $luaMarker = $resolvedMarker -replace '\\', '/'
    $command = 'rom011_marker_path = [[' + $luaMarker + ']]; '
}
$command += 'dofile([[' + ($resolvedLua -replace '\\', '/') + ']])'
if ($PostCommand) {
    $command += '; ' + $PostCommand
}
if ($resolvedReady) {
    $luaReady = $resolvedReady -replace '\\', '/'
    $command += '; local f=assert(io.open([[' + $luaReady + ']], [[w]])); ' +
        'f:write([[ready]]); f:close()'
}
$prompt.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($command)

$invokeScript = Join-Path $PSScriptRoot 'invoke_mgba_run.ps1'
$invokeArguments = @(
    '-NoProfile',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $invokeScript,
    '-TargetProcessId',
    [string]$TargetProcessId
)
$invokeProcess = $null
try {
    $invokeProcess = Start-Process `
        -FilePath 'powershell.exe' `
        -ArgumentList $invokeArguments `
        -WindowStyle Hidden `
        -PassThru
    if ($resolvedReady) {
        $readyConfirmed = $false
        for ($attempt = 0; $attempt -lt 100 -and -not $readyConfirmed; $attempt++) {
            if ((Test-Path -LiteralPath $resolvedReady) -and
                [System.IO.File]::ReadAllText($resolvedReady) -eq 'ready') {
                $readyConfirmed = $true
                break
            }
            $invokeProcess.Refresh()
            if ($invokeProcess.HasExited -and $invokeProcess.ExitCode -ne 0) {
                throw 'Asynchronous Run invocation failed'
            }
            Start-Sleep -Milliseconds 100
        }
        if (-not $readyConfirmed) {
            throw 'Lua script did not report ready'
        }
    } else {
        if (-not $invokeProcess.WaitForExit(10000)) {
            throw 'Asynchronous Run invocation did not complete'
        }
        if ($invokeProcess.ExitCode -ne 0) {
            throw 'Asynchronous Run invocation failed'
        }
    }
} finally {
    if ($invokeProcess) {
        $invokeProcess.Refresh()
        if (-not $invokeProcess.HasExited) {
            Stop-Process -Id $invokeProcess.Id -Force -ErrorAction SilentlyContinue
            $invokeProcess.WaitForExit(5000) | Out-Null
        }
    }
}
