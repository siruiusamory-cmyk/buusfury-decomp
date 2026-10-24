; PATH-100-009 / R-RAW-001: the census run 0x0877af34..0x0877af50 as LABELED RAW DATA.

	EXPORT	|unk_0877AF34|
|unk_0877AF34|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x77af34_0x77af38.extracted
	EXPORT	|unk_0877AF38|
|unk_0877AF38|
; cited by 0x080395AA ldr r0 +0x8, 0x080395D0 ldr r0 +0x8, 0x08039600 ldr r0 +0x8, 0x080396AE ldr r5 +0x4 ldr r5 +0x8 (+1 more sites)

	INCBIN	baserom.gba_0x77af38_0x77af44.extracted
	EXPORT	|unk_0877AF44|
|unk_0877AF44|
; cited by 0x080397F2 ldr r0 +0x4, 0x0803982C ldr r0 +0x0

	DCD	|g_KeyState|
	DCD	|unk_0807012C|
	EXPORT	|unk_0877AF4C|
|unk_0877AF4C|
; cited by 0x080398AE ldr r0 +0x0


	INCBIN	baserom.gba_0x77af4c_0x77af50.extracted
