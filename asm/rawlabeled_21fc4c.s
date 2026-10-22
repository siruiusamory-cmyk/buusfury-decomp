; PATH-100-006 / R-RAW-001: the census run 0x0821fc4c..0x082205f8 as LABELED RAW DATA.

	EXPORT	|unk_0821FC4C|
|map_anim_row_0821FC4C|
|unk_0821FC4C|
; no citation: the run's first byte, a label boundary only

	DCB 0x04,0x03
	DCW 0x037d
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|unk_0821FC60|
	INCBIN  build\animframe\gen_21fc60_21fd7c.bin
	EXPORT	|unk_0821FD7C|
|unk_0821FD7C|
; cited by 0x082797C6

	INCBIN	baserom.gba_0x21fd7c_0x22002c.extracted
	EXPORT	|unk_0822002C|
|unk_0822002C|
; cited by 0x0836F848

	INCBIN	baserom.gba_0x22002c_0x220498.extracted
	EXPORT	|unk_08220498|
|unk_08220498|
; cited by 0x08614034 ldr r0 +0x38 ldrh r0 +0x12 ldrh r0 +0x3c str r0 +0x8


	INCBIN  baserom.gba_0x220498_0x220588.extracted
|map_anim_row_08220588|
|unk_08220588|
	DCB 0x12,0x17
	DCW 0x0366
	DCD 0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c,0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c
	DCD 0x0821fc60,0x0821fd7c,0x0821fee8,0x0821fd7c,0x0821fc60,0x0821fd7c,0x0821fee8,0x082200a0
	DCD 0x08220288,0x08220434
|unk_082205D4|
	INCBIN  baserom.gba_0x2205d4_0x2205dc.extracted
|unk_082205DC|
	INCBIN	build\mapcontainer\map_002205DC_002205F4.bin
|unk_082205F4|
	INCBIN	build\mapcontainer\map_002205F4_002205F8.bin
