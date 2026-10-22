	CODE16
|sub_0800F3F8|
	PUSH     {r3, lr}
	ADD      r1, r0, #0
	LDRH     r0, [r0, #0xc]
	LDR      r2, [pc, #0xb4]
	LSL      r0, r0, #5
	ADD      r0, r0, r2
	ADD      r1, #0x44
	LDMIA    r1!, {r1, r2}
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r3, pc}
