	CODE16
|sub_0803A7EA|
|unk_0803A7EA|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x5628
	INCBIN  baserom.gba_0x3a7ee_0x3a7f2.extracted
	CODE16
|dat_0803A7F2|
	DCW      0x0000
|unk_0803A7F4|
	INCBIN	baserom.gba_0x3a7f4_0x3a7f6.extracted
	LSR      r7, r6, #1
	ADD      r2, #0xd8
	LSL      r0, r0, #0xc

