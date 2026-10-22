	CODE16
|sub_0803725A|
	LSR      r4, r0, #0x20
	STRH     r0, [r4, #6]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LDR      r1, [pc, #0x200]
	PUSH     {r4}
	LDR      r1, [r1, #8]
	LDR      r3, [r0, #0x1c]
	ADD      r1, #0x18
	LDR      r4, [r1]
	SUB      sp, #8
	SUB      r3, r3, r4
	LDR      r4, [r0, #0x20]
	LDR      r1, [r1, #4]
	ADD      r2, r0, #0
	SUB      r1, r4, r1
	STR      r1, [sp, #4]
	ADD      r2, #0x24
	ADD      r1, r3, #0
	STR      r3, [sp]
	LDR      r3, [sp, #4]
	STMIA    r2!, {r1, r3}
	LDR      r1, [r0, #0x20]
	STR      r1, [r0, #4]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
