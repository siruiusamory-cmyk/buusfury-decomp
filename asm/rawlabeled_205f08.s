; PATH-100-006 / R-RAW-001: the census run 0x08205f08..0x08205f78 as LABELED RAW DATA.

	EXPORT	|unk_08205F08|
|unk_08205F08|
; no citation: the run's first byte, a label boundary only

	INCBIN	build\mapcontainer\map_00205F08_00205F68.bin
	EXPORT	|unk_08205F68|
|unk_08205F68|
; cited by 0x08205BC6 strh r1 +0x22


	INCBIN	build\mapcontainer\map_00205F68_00205F78.bin
