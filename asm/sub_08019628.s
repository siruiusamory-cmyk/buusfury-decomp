	CODE16
|sub_08019628|
	PUSH     {r3, lr}
	LDRB     r1, [r0, #0x18]
	LDRB     r2, [r0, #0x17]
	ADD      r1, r1, r2
	LSL      r1, r1, #0x18
	ASR      r1, r1, #0x18
	MOV      r2, #7
	MVN      r2, r2
	CMP      r1, r2
	STRB     r1, [r0, #0x18]
	BGE      |sub_0801964A|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x158]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	POP      {r3, pc}
