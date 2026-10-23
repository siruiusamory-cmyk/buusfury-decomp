	CODE16
|sub_080355C2|
	LSL      r0, r0, #0
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	DCW      0xfe80,0xffff,0xb210
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080355E4|
	LDR      r1, [pc, #4]
	STR      r1, [r0]
|loc_080355E4|
	POP      {r3, pc}
|sub_080355E6|
|unk_080355E6|
	INCBIN	baserom.gba_0x355e6_0x355ea.extracted
|sub_080355EA|
	DCW      0x0804
