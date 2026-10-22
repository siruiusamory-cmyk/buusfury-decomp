; PATH-100-009 / R-RAW-001: the census run 0x0874f080..0x0875023c as LABELED RAW DATA.

	EXPORT	|unk_0874F080|
|unk_0874F080|
; cited by 0x0805200E ldr r0 +0x4

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_0874F08C|
|unk_0874F08C|
; cited by 0x080293E8 INDEXED ldr [r3 + reg] INDEXED base + register (r1, r1, r3) ldr r0 +0x0 INDEXED base + register (r0, r0, r4), 0x080293FA ldr r0 +0x0, 0x08029456 ldr r7 +0x4, 0x0802948E ldr r7 +0x8 ldm r7 +0x0 ldr r7 +0x4 ldr r7 +0x0 (+2 more sites)

	INCBIN	baserom.gba_0x74f08c_0x7501ec.extracted
	EXPORT	|unk_087501EC|
|unk_087501EC|
; cited by 0x080293B2 INDEXED ldr [r3 + reg] INDEXED base + register (r1, r1, r3) ldr r0 +0x0 INDEXED base + register (r0, r0, r4)

	INCBIN	baserom.gba_0x7501ec_0x750204.extracted
	EXPORT	|unk_08750204|
|unk_08750204|
; cited by 0x08029410, 0x080294AA ldr r7 +0x4 ldr r7 +0x0 INDEXED base + register (r1, r0, r1) INDEXED base + register (r0, r0, r7), 0x0802951A ldr r0 +0x4c, 0x0802956A ldr r4 +0x4

	INCBIN	baserom.gba_0x750204_0x75021c.extracted
	EXPORT	|unk_0875021C|
|unk_0875021C|
; cited by 0x08029708 INDEXED ldr [r2 + reg] INDEXED base + register (r1, r1, r2)


	INCBIN	baserom.gba_0x75021c_0x75023c.extracted
