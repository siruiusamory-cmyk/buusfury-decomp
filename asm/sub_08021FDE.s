	CODE16
|sub_08021FDE|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x81
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x18]
	CMP      r0, #0
	BNE      |loc_080220AA|
	LDR      r0, [r4, #0x14]
	LDR      r7, [pc, #0xd8]
	CMP      r0, #0
	BNE      |sub_08022006|
	ADD      r0, r5, #0
	BL       |loc_08021F0A|
	CMP      r0, #0
	BNE      |sub_08022006|
	MOV      r1, #1
	STR      r1, [r7, #0xc]
	POP      {r3, r4, r5, r6, r7, pc}
