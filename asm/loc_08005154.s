	CODE16
|loc_08005154|
	PUSH     {r3, r4, r5, r6, r7, lr}
	SUB      r6, r3, r1
	LDR      r3, [r0, #0x24]
	ADD      r5, r0, #0
	LDR      r0, [r0, #0x28]
	MUL      r0, r2
	ADD      r0, r3, r0
	ADD      r4, r0, r1
	MOV      r0, #0x2f
	SUB      r2, r6, #2
	ADD      r7, r2, #0
	STRB     r0, [r4]
	MOV      r1, #0x30
	ADD      r0, r4, #1
	BL       |inc_0x046118_0x049114| + 0xd28
	ADD      r1, r4, r6
	SUB      r1, #0x10
	MOV      r0, #0x31
	STRB     r0, [r1, #0xf]
	LDR      r0, [r5, #0x28]
	SUB      r0, r4, r0
	ADD      r0, #1
	ADD      r2, r7, #0
	MOV      r1, #0x2f
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r5, #0x28]
	ADD      r0, r0, r4
	ADD      r0, #1
	ADD      r2, r7, #0
	MOV      r1, #0x31
	BL       |inc_0x046118_0x049114| + 0xd28
	POP      {r3, r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LSL      r1, r0, #4
	LSL      r1, r0, #4
	ADD      r1, #0x31
	ADD      r1, #0x31
	ADD      r1, r0, #4
	SUB      r7, #0x6e
	LDR      r5, [r3, #0x60]
	LSL      r7, r7, #4
	ADD      r0, #1
	LSL      r0, r0, #0
