; PATH-100-005 / R-RAW-001: the census run 0x08754978..0x08756a4c as LABELED RAW DATA.

	EXPORT	|unk_08754978|
|unk_08754978|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x754978_0x75497c.extracted
	EXPORT	|unk_0875497C|
|unk_0875497C|
; cited by 0x0802C7CC INDEXED ldr [r2 + reg] INDEXED base + register (r0, r0, r2) INDEXED base + register (r0, r0, r1), 0x0802C820, 0x0802C8E2

	INCBIN	baserom.gba_0x75497c_0x754a1c.extracted
	EXPORT	|unk_08754A1C|
|unk_08754A1C|
; cited by 0x0802C7CA INDEXED ldr [r2 + reg] INDEXED base + register (r0, r0, r2) INDEXED base + register (r0, r0, r1), 0x0802C806 INDEXED base + register (r0, r0, r1)

	INCBIN	baserom.gba_0x754a1c_0x756a04.extracted
	EXPORT	|unk_08756A04|
|unk_08756A04|
; cited by 0x0801B662 INDEXED base + register (r0, r0, r2) INDEXED base + register (r0, r0, r4)

	INCBIN	baserom.gba_0x756a04_0x756a2c.extracted
	EXPORT	|unk_08756A2C|
|unk_08756A2C|
; cited by 0x0802CBDA INDEXED base + register (r4, r0, r1) ldr r0 +0x0, 0x0802CC28 ldr r0 +0x0, 0x0802CC56 ldr r0 +0x0, 0x0802CC84 ldr r0 +0x0 (+2 more sites)


	INCBIN	baserom.gba_0x756a2c_0x756a4c.extracted
