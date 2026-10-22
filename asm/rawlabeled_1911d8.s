; PATH-100-006 / R-RAW-001: the census run 0x081911d8..0x081912e4 as LABELED RAW DATA.

	EXPORT	|unk_081911D8|
|unk_081911D8|
; cited by 0x082807EE

	INCBIN	build\animframe\gen_1911d8_191214.bin
	EXPORT	|unk_08191214|
|unk_08191214|
; cited by 0x0827F662 INDEXED str [r2 + reg]

	INCBIN	build\animframe\gen_191214_191250.bin
	EXPORT	|unk_08191250|
|map_anim_row_08191250|
|unk_08191250|
; cited by 0x08191168, 0x081911B8

	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081911d8,0x08191214
	EXPORT	|unk_0819125C|
|unk_0819125C|
; cited by 0x082865F0 ldm r0 +0x0

	INCBIN	build\animframe\gen_19125c_191288.bin
	EXPORT	|unk_08191288|
|unk_08191288|
; cited by 0x081BE08A INDEXED strh [r1 + reg]


	INCBIN  build\animframe\gen_191288_1912b4.bin
|map_anim_row_081912B4|
|unk_081912B4|
	DCB 0x02,0x01
	DCW 0x037d
	DCD 0x0819125c,0x08191288
|unk_081912C0|
	INCBIN  baserom.gba_0x1912c0_0x1912c8.extracted
|unk_081912C8|
	INCBIN	build\mapcontainer\map_001912C8_001912E0.bin
|unk_081912E0|
	INCBIN	build\mapcontainer\map_001912E0_001912E4.bin
