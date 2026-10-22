	CODE16
|sub_08017696|
	LSR      r3, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r7, sp, #0x3e0
	LSR      r4, r0, #0x20
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x20c]
	MOV      r2, #1
	STR      r0, [r4]
	ADD      r0, r4, #4
	LSL      r2, r2, #9
	MOV      r1, #5
	LSL      r1, r1, #0x18
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r0, #0x81
	LSL      r0, r0, #2
	ADD      r0, r4, r0
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x1f4]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r0, r4, #0
	POP      {r4, pc}
