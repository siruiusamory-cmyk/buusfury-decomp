; PATH-100-006 / R-RAW-001: the census run 0x082346d0..0x0823475c as LABELED RAW DATA.

	EXPORT	|unk_082346D0|
|unk_082346D0|
; no citation: the run's first byte, a label boundary only

	INCBIN	build\mapcontainer\map_002346D0_002346E8.bin
	EXPORT	|unk_082346E8|
|unk_082346E8|
; cited by 0x082345D6 strh r4 +0x3a INDEXED ldrb [r3 + reg] ldrb r4 +0x9 strh r4 +0x3c

	INCBIN	build\mapcontainer\map_002346E8_00234758.bin
|unk_08234758|
	INCBIN	build\mapcontainer\map_00234758_0023475C.bin
