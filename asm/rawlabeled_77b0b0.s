; PATH-100-009 / R-RAW-001: the census run 0x0877b0b0..0x0877b0f8 as LABELED RAW DATA.

	EXPORT	|unk_0877B0B0|
|unk_0877B0B0|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x77b0b0_0x77b0d0.extracted
	EXPORT	|unk_0877B0D0|
|unk_0877B0D0|
; cited by 0x0803A63A INDEXED ldr [r6 + reg] INDEXED base + register (r0, r0, r6) INDEXED base + register (r2, r0, r1), 0x0803A63E INDEXED ldr [r6 + reg] INDEXED base + register (r0, r0, r6) INDEXED base + register (r2, r0, r1), 0x0803A678


	INCBIN	baserom.gba_0x77b0d0_0x77b0f8.extracted
