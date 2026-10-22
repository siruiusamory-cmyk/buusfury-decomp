; PATH-100-005 / R-RAW-001: the census run 0x0875029c..0x08752d4c as LABELED RAW DATA.

	EXPORT	|unk_0875029C|
|unk_0875029C|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x75029c_0x75043c.extracted
	EXPORT	|unk_0875043C|
|unk_0875043C|
; cited by 0x0802A37A INDEXED base + register (r1, r1, r3) INDEXED base + register (r0, r0, r1) INDEXED base + register (r0, r0, r5)

	INCBIN	build\endrom\endrom_0075043C_007504CC.bin
	EXPORT	|unk_087504CC|
|unk_087504CC|
; cited by 0x08052636 ldr r0 +0x0

	INCBIN	baserom.gba_0x7504cc_0x7520d4.extracted
	EXPORT	|unk_087520D4|
|unk_087520D4|
; cited by 0x0801C472

	INCBIN	baserom.gba_0x7520d4_0x752d28.extracted
	EXPORT	|unk_08752D28|
|unk_08752D28|
; cited by 0x0801C4CA INDEXED base + register (r1, r1, r2)


	INCBIN	baserom.gba_0x752d28_0x752d4c.extracted
