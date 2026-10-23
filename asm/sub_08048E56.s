	CODE16
|sub_08048E56|
	LSR      r4, r0, #0x20
	SUB      r0, r6, r3
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r1, [pc, #0x14]
	LDR      r0, [pc, #0xc]
	STR      r0, [r1]
	BX       lr
|loc_08048E6A|
	DCW      0x0000
	DCW      0x9af0,0x0804,0x1c44,0x0300,0xe454
|loc_08048E76|
	LSR      r4, r0, #0x20
	CMP      r2, #0x4c
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	LDR      r1, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048E84|
|unk_08048E84|
	INCBIN	baserom.gba_0x48e84_0x48e86.extracted
|sub_08048E86|
	DCW      0x0804
	DCW      0x2bd4
	DCW      0x0300
	DCW      0x4805
