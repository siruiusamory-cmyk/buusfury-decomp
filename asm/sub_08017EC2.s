	CODE16
|sub_08017EC2|
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [pc, #0x3a0]
	ADD      r4, r0, #0
	LDR      r1, [r4, #0x60]
	LDR      r0, [r5, #8]
	LDR      r2, [pc, #0x39c]
	LDR      r1, [r1, #0xc]
	ADD      r0, r0, r2
	LDR      r2, [r0]
	ADD      r1, r2, r1
|loc_08017ED6|
	STR      r1, [r0]
	LDR      r2, [r0]
	CMP      r2, r1
	BNE      |loc_08017ED6|
	MOV      r1, #0x21
	LDR      r2, [pc, #0x38c]
	LSL      r1, r1, #4
	ADD      r1, r1, r2
	LDR      r6, [pc, #0x38c]
	LDR      r0, [r5]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r6
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r1, r4, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x10]
	BL       |sub_08017EC2|
	LDR      r0, [pc, #0x35c]
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x10]
	BL       |inc_0x0158_0x143f2| + 0x12532
	POP      {r4, pc}
	PUSH     {r4}
	LDMIA    r1!, {r3, r4}
	STR      r3, [r0, #0x48]
	STR      r4, [r0, #0x4c]
	LDR      r2, [r0, #0x60]
	SUB      r1, #8
	LDRB     r4, [r2]
	LDR      r3, [r1]
	LSR      r4, r4, #1
	SUB      r3, r3, r4
	STR      r3, [r0, #0x38]
	LDRB     r2, [r2]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x40]
	LDR      r1, [r1, #4]
	STR      r1, [r0, #4]
	POP      {r4}
	BX       lr
	PUSH     {r4, r5}
	LDR      r4, [r2]
	LDR      r5, [r1, #4]
	LDR      r2, [r2, #4]
	LDR      r3, [r1, #8]
	SUB      sp, #8
	ADD      r4, r4, r5
	ADD      r2, r2, r3
	STR      r2, [sp, #4]
	STR      r4, [sp]
	LDRB     r1, [r1]
	LSR      r1, r1, #1
	SUB      r1, r4, r1
	STMIA    r0!, {r1, r2}
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
