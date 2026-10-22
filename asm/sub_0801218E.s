	CODE16
|sub_0801218E|
	LSR      r7, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	SUB      r1, #0x3c
	LSR      r7, r5, #1
	LDR      r6, [sp, #0x210]
	LSR      r4, r0, #0x20
	LSR      r0, r1, #0x20
	LSL      r0, r0, #0
	LDMIA    r5!, {r2, r4, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r6, [sp, #0x240]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r1, #8
	SUB      sp, #0x70
	MOV      r0, #0
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x48]
	ADD      r0, sp, #4
	ADD      r6, sp, #4
	BL       |loc_08004038|
	ADD      r0, r6, #4
	STR      r0, [sp]
	ADD      r0, r5, #0
	ADD      r0, #8
	LDR      r1, [r4, #4]
	ADD      r4, r0, #0
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x3f8
	ADD      r0, r4, #0
	ADD      sp, #0x70
	POP      {r4, r5, r6, pc}
