; PATH-100-009 / R-RAW-001: the census run 0x08757390..0x08757a40 as LABELED RAW DATA.

	EXPORT	|unk_08757390|
|unk_08757390|
; no citation: the run's first byte, a label boundary only

	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_08757398|
|unk_08757398|
; cited by 0x08051222 ldr r0 +0x0

	DCD	|unk_03001C4C|
	DCD	|unk_0807012C|
	EXPORT	|unk_087573A0|
|unk_087573A0|
; cited by 0x0802E6B2 ldr r0 +0x0, 0x0802E6BC ldr r0 +0x0, 0x0802E6CE ldr r5 +0x0, 0x0802E6FA ldr r0 +0x0 (+3 more sites)

	INCBIN	baserom.gba_0x7573a0_0x7579b8.extracted
	EXPORT	|unk_087579B8|
|unk_087579B8|
; cited by 0x0802E50C

	INCBIN	baserom.gba_0x7579b8_0x757a30.extracted
	EXPORT	|unk_08757A30|
|unk_08757A30|
; cited by 0x0802E87C ldr r5 +0xc ldr r5 +0x8 ldr r2 +0x8, 0x0802E8C6 ldr r2 +0x8 INDEXED base + register (r0, r0, r1) ldr r3 +0x8, 0x0802E920 ldr r3 +0x8, 0x0802E9E6 ldr r7 +0xc ldr r7 +0x4


	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03001068|
	DCD	|unk_03001C4C|
