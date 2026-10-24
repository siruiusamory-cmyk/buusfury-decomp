; PATH-100-009 / R-RAW-001: the census run 0x087592bc..0x08759324 as LABELED RAW DATA.

	EXPORT	|unk_087592BC|
|unk_087592BC|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x7592bc_0x7592dc.extracted
	EXPORT	|unk_087592DC|
|unk_087592DC|
; cited by 0x080333AC INDEXED base + register (r3, r2, r3) INDEXED base + register (r2, r2, r3), 0x080333B8 INDEXED base + register (r2, r2, r3), 0x080333FA INDEXED base + register (r1, r0, r1), 0x08033442 INDEXED base + register (r1, r0, r1) INDEXED base + register (r0, r0, r1) INDEXED base + register (r2, r0, r1) (+11 more sites)

	INCBIN	baserom.gba_0x7592dc_0x75930c.extracted
	EXPORT	|unk_0875930C|
|unk_0875930C|
; cited by 0x0803363A ldr r0 +0xc, 0x08033674 ldr r0 +0x8, 0x08033786 ldr r5 +0x0 ldr r5 +0x4 INDEXED base + register (r0, r0, r7)

	DCD	|g_KeyState|
	DCD	|unk_03003898|
	DCD	|unk_0806EE6C|
	DCD	|unk_0806E050|
	EXPORT	|unk_0875931C|
|unk_0875931C|
; cited by 0x08033890 ldr r1 +0x0

	INCBIN	baserom.gba_0x75931c_0x759320.extracted
	EXPORT	|unk_08759320|
|unk_08759320|
; cited by 0x0804E896 ldr r6 +0x0


	INCBIN	baserom.gba_0x759320_0x759324.extracted
