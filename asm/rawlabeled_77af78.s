; PATH-100-009 / R-RAW-001: the census run 0x0877af78..0x0877afc0 as LABELED RAW DATA.

	EXPORT	|unk_0877AF78|
|unk_0877AF78|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x77af78_0x77af98.extracted
	EXPORT	|unk_0877AF98|
|unk_0877AF98|
; cited by 0x08039A1A ldm r0 +0x0 ldm r0 +0x0, 0x08039AA0, 0x08039ABC INDEXED base + register (r2, r0, r1), 0x08039AF0 INDEXED base + register (r2, r0, r1) (+2 more sites)


	INCBIN	baserom.gba_0x77af98_0x77afc0.extracted
