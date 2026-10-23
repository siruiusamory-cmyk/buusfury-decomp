	CODE16
|unk_08053160|
	CODE32
	LDR      r3, [pc, #0x10]
	UMULL    r1, r2, r3, r0
	LDR      r3, [pc, #0xc]
	MOV      r1, r2, LSR #7
	MLA      r0, r3, r1, r0
	BX       lr
	CODE16
	CODE16
|unk_08053178|
	INCBIN	baserom.gba_0x53178_0x5317a.extracted
	CODE16
|dat_0805317A|
	DCW      0x0576
	DCW      0xe890
	DCW      0xffff
	DCW      0x4778
	DCW      0x0000

