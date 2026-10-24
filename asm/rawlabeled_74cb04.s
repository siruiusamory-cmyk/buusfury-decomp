; PATH-100-006 / R-RAW-001: the census run 0x0874cb04..0x0874d044 as LABELED RAW DATA.

	EXPORT	|unk_0874CB04|
|unk_0874CB04|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x74cb04_0x74cf24.extracted
	EXPORT	|unk_0874CF24|
|unk_0874CF24|
; cited by 0x08026DB2 ldr r0 +0x0

	INCBIN	baserom.gba_0x74cf24_0x74cf28.extracted
	EXPORT	|unk_0874CF28|
|unk_0874CF28|
; cited by 0x0805298A ldr r0 +0x0

	INCBIN	baserom.gba_0x74cf28_0x74d02c.extracted
	EXPORT	|unk_0874D02C|
|unk_0874D02C|
; cited by 0x08026F4E ldr r2 +0x0 ldr r2 +0x8 ldr r2 +0x4 ldr r2 +0xc

	INCBIN	baserom.gba_0x74d02c_0x74d03c.extracted
	EXPORT	|unk_0874D03C|
|unk_0874D03C|
; cited by 0x08052912 ldr r0 +0x4


	DCD	|g_KeyState|
	DCD	|unk_03001C4C|
