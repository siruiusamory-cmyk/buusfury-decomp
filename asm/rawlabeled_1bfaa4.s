; PATH-100-006 / R-RAW-001: the census run 0x081bfaa4..0x081bfe30 as LABELED RAW DATA.

	EXPORT	|unk_081BFAA4|
|map_anim_row_081BFAA4|
|unk_081BFAA4|
; no citation: the run's first byte, a label boundary only

	DCB 0x02,0x02
	DCW 0x037e
	DCD 0x081911d8,0x08191214
|map_anim_row_081BFAB0|
|unk_081BFAB0|
	DCB 0x04,0x03
	DCW 0x037b
	DCD 0x0819b130,0x0819b0ac,0x0819b0d8,0x0819b104
|map_anim_row_081BFAC4|
|unk_081BFAC4|
	DCB 0x10,0x0b
	DCW 0x0370
	DCD 0x0817a9ac,0x0817aaac,0x0817abac,0x0817aca4,0x0817a9ac,0x0817aaac,0x0817ada4,0x0817aaac
	DCD 0x0817aea4,0x0817aaac,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4
|unk_081BFB08|
	INCBIN  build\animframe\gen_1bfb08_1bfd4c.bin
|map_anim_row_081BFD4C|
|unk_081BFD4C|
	DCB 0x04,0x0e
	DCW 0x0362
	DCD 0x081bfb08,0x081bfbd0,0x081bfc8c,0x081bfbd0
	EXPORT	|unk_081BFD60|
|unk_081BFD60|
; cited by 0x082817E2

	INCBIN	build\animframe\gen_1bfd60_1bfd9c.bin
	EXPORT	|unk_081BFD9C|
|unk_081BFD9C|
; cited by 0x0826FBB6 INDEXED strb [r1 + reg]


	INCBIN  build\animframe\gen_1bfd9c_1bfdd8.bin
|map_anim_row_081BFDD8|
|unk_081BFDD8|
	DCB 0x02,0x02
	DCW 0x0360
	DCD 0x081bfd60,0x081bfd9c
|unk_081BFDE4|
	INCBIN  baserom.gba_0x1bfde4_0x1bfdf8.extracted
|unk_081BFDF8|
	INCBIN	build\mapcontainer\map_001BFDF8_001BFE28.bin
|unk_081BFE28|
	INCBIN	build\mapcontainer\map_001BFE28_001BFE30.bin
