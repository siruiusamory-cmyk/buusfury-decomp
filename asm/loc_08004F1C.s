	CODE16
|loc_08004F1C|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	LDR      r4, [sp, #0x28]
	LDR      r3, [r0, #0x24]
	ADD      r7, r0, #0
	LDR      r0, [r0, #0x28]
	LDR      r6, [pc, #0x270]
	MUL      r0, r2
	ADD      r0, r3, r0
	ADD      r5, r0, r1
	CMP      r4, #0
	BEQ      |loc_08004F4C|
|loc_08004F34|
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x10]
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [r7, #0x28]
	SUB      r4, #1
	ADD      r5, r0, r5
	LDR      r0, [pc, #0x258]
	EOR      r6, r0
	CMP      r4, #0
	BNE      |loc_08004F34|
|loc_08004F4C|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
