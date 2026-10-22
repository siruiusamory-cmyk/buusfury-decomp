	CODE16
|sub_0800CA0A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r6, #1
	ADD      r3, r2, #4
	CMP      r1, #0
	LDR      r0, [r0, #0x2c]
	BEQ      |sub_0800CA5C|
	CMP      r1, #2
	BEQ      |loc_0800CAB2|
	CMP      r1, #4
	LDR      r3, [r0]
	BNE      |loc_0800CAF6|
	LDR      r5, [r3, #0x24]
	ADD      r3, r5, r3
	BL       |inc_0x046118_0x049114| + 0x98e
	ADD      r7, r0, #0
	LDR      r0, [pc, #0xd8]
	LDR      r1, [r4, #0x2c]
	SUB      r0, #8
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0x1c]
	ADD      r5, r4, #0
	ADD      r5, #0x14
	CMP      r1, #0
	BEQ      |loc_0800CA40|
	MOV      r6, #0
|loc_0800CA40|
	ADD      r4, r0, #0
	ADD      r4, #0x80
	ADD      r2, r6, #0
	ADD      r0, r5, #0
	LDR      r1, [r4, #0x28]
	BL       |loc_08009930|
	ADD      r2, r6, #0
	ADD      r0, r5, #0
	LDR      r1, [r4, #0x30]
	BL       |loc_08009930|
	ADD      r0, r7, #0
	POP      {r3, r4, r5, r6, r7, pc}
