; PATH-100-009 / R-RAW-001: the census run 0x0875919c..0x087591dc as LABELED RAW DATA.

	EXPORT	|unk_0875919C|
|unk_0875919C|
; no citation: the run's first byte, a label boundary only

	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03001068|
	EXPORT	|unk_087591A8|
|unk_087591A8|
; cited by 0x08031884, 0x0803188C, 0x0803192E INDEXED base + register (r0, r2, r0) INDEXED base + register (r5, r0, r1) INDEXED base + register (r0, r0, r1) INDEXED ldr [r2 + reg], 0x08031B58

	INCBIN	baserom.gba_0x7591a8_0x7591b8.extracted
	EXPORT	|unk_087591B8|
|unk_087591B8|
; cited by 0x08031EC8 ldr r0 +0xc INDEXED base + register (r0, r0, r1) ldr r7 +0xc, 0x08031F00 INDEXED base + register (r0, r0, r1) ldr r7 +0xc INDEXED base + register (r7, r0, r1) ldr r0 +0xc, 0x08031F64 ldr r0 +0xc, 0x08032008 ldr r0 +0xc

	DCD	|g_KeyState|
	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03001068|
	EXPORT	|unk_087591C8|
|unk_087591C8|
; cited by 0x080321F8 ldr r0 +0x8, 0x08032200 ldr r0 +0x8, 0x080324C6 ldr r0 +0xc INDEXED ldr [r5 + reg], 0x08032566 ldr r0 +0xc INDEXED base + register (r0, r0, r1) INDEXED ldr [r5 + reg]

	INCBIN	baserom.gba_0x7591c8_0x7591d8.extracted
	EXPORT	|unk_087591D8|
|unk_087591D8|
; cited by 0x080327EA ldr r0 +0x0


	INCBIN	baserom.gba_0x7591d8_0x7591dc.extracted
