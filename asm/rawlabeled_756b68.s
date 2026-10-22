; PATH-100-009 / R-RAW-001: the census run 0x08756b68..0x087572ac as LABELED RAW DATA.

	EXPORT	|unk_08756B68|
|unk_08756B68|
; no citation: the run's first byte, a label boundary only

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_08756B74|
|unk_08756B74|
; cited by 0x0802D7FC INDEXED base + register (r1, r2, r0) INDEXED ldr [r0 + reg] INDEXED ldr [r7 + reg], 0x0802D840 INDEXED ldr [r7 + reg], 0x0802D8A6, 0x0802D90C (+1 more sites)

	INCBIN	baserom.gba_0x756b74_0x7571f4.extracted
	EXPORT	|unk_087571F4|
|unk_087571F4|
; cited by 0x0802D7E2 INDEXED base + register (r1, r1, r2) INDEXED base + register (r1, r2, r0) INDEXED ldr [r0 + reg] INDEXED ldr [r7 + reg], 0x0802D866

	INCBIN	baserom.gba_0x7571f4_0x757284.extracted
	EXPORT	|unk_08757284|
|unk_08757284|
; cited by 0x0802DBEA ldr r5 +0x4, 0x0802DC34 INDEXED base + register (r0, r0, r3) ldr r6 +0x4, 0x0802DC4E INDEXED base + register (r0, r0, r3)


	INCBIN	baserom.gba_0x757284_0x7572ac.extracted
