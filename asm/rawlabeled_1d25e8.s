; PATH-100-006 / R-RAW-001: the census run 0x081d25e8..0x081d2798 as LABELED RAW DATA.

	EXPORT	|unk_081D25E8|
|unk_081D25E8|
; no citation: the run's first byte, a label boundary only

	INCBIN	build\mapcontainer\map_001D25E8_001D2618.bin
|unk_081D2618|
	INCBIN	build\animframe\gen_1d2618_1d2650.bin
	EXPORT	|unk_081D2650|
|unk_081D2650|
; cited by 0x081D4A98 INDEXED base + register (r1, r2, r7)

	INCBIN	build\animframe\gen_1d2650_1d268c.bin
	EXPORT	|unk_081D268C|
|unk_081D268C|
; cited by 0x081D6FFC ldr r6 +0x54

	INCBIN	baserom.gba_0x1d268c_0x1d2711.extracted
	EXPORT	|unk_081D2711|
|unk_081D2711|
; cited by 0x083085C8

	INCBIN	baserom.gba_0x1d2711_0x1d2754.extracted
	EXPORT	|unk_081D2754|
|unk_081D2754|
; cited by 0x081D24A0


	INCBIN	build\mapcontainer\map_001D2754_001D2794.bin
|unk_081D2794|
	INCBIN	build\mapcontainer\map_001D2794_001D2798.bin
