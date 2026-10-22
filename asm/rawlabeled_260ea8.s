; PATH-100-006 / R-RAW-001: the census run 0x08260ea8..0x08261130 as LABELED RAW DATA.

	EXPORT	|unk_08260EA8|
|unk_08260EA8|
; no citation: the run's first byte, a label boundary only

	INCBIN	build\animframe\gen_260ea8_260f1c.bin
	EXPORT	|unk_08260F1C|
|unk_08260F1C|
; cited by 0x08260CF4 str r5 +0x7c

	INCBIN	build\animframe\gen_260f1c_261004.bin
	EXPORT	|unk_08261004|
|unk_08261004|
; cited by 0x08260E7C ldrh r1 +0x1e INDEXED ldrsh [r4 + reg]


	INCBIN	build\animframe\gen_261004_2610ec.bin
|unk_082610EC|
	INCBIN	build\mapcontainer\map_002610EC_0026112C.bin
|unk_0826112C|
	INCBIN	build\mapcontainer\map_0026112C_00261130.bin
