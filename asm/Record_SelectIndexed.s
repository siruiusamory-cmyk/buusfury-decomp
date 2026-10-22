	CODE16
|Record_SelectIndexed|
	LDR      r2, [r0, #0x58]
	LSL      r1, r1, #2
	ADD      r3, r2, r1
	LDR      r3, [r3, #0x54]
	STR      r3, [r0, #0x50]
	LDR      r2, [r2, #0x50]
	CMP      r2, #0
	BEQ      |loc_0800ECEE|
	LDR      r1, [r2, r1]
	STR      r1, [r0, #0x4c]
|loc_0800ECEE|
	BX       lr
	LDR      r2, [pc, #0xec]
	PUSH     {r4, lr}
	ADD      r2, #0x88
	LDRB     r3, [r2, r1]
	LDR      r2, [r0, #0x58]
	LSL      r3, r3, #2
	ADD      r4, r2, r3
	LDR      r4, [r4, #0x54]
	STR      r4, [r0, #0x50]
	LDR      r2, [r2, #0x50]
	CMP      r2, #0
	BEQ      |loc_0800ED0C|
	LDR      r2, [r2, r3]
	STR      r2, [r0, #0x4c]
|loc_0800ED0C|
	LDR      r2, [r0]
	LDR      r3, [r2, #0x2c]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
