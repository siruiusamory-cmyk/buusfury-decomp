	CODE16
|sub_0804FDE6|
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	LDRB     r0, [r4]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_0804FE12|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x18]
	CMP      r0, r1
	BEQ      |loc_0804FE12|
	MOV      r3, #2
	LDR      r0, [pc, #0x14]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_0804FE12|
	POP      {r4, pc}
|sub_0804FE14|
|unk_0804FE14|
	INCBIN	baserom.gba_0x4fe14_0x4fe16.extracted
