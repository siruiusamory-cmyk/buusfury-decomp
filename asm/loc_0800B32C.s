	CODE16
|loc_0800B32C|
	LDR      r1, [pc, #0x1ec]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1e
	LSR      r2, r1, #0x1f
	ADD      r1, r0, #0
	ADD      r1, #0x80
	CMP      r2, #0
	BEQ      |loc_0800B34C|
	MOV      r2, #0
	LDR      r3, [pc, #0x1dc]
	MVN      r2, r2
	STR      r2, [r3]
	LDR      r2, [pc, #0x1d8]
	STR      r2, [r1, #0x34]
|loc_0800B34C|
	LDR      r1, [r1, #0x34]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r2, [r1, #0x34]
	LDR      r3, [r1, #0x68]
	LSL      r2, r2, #1
	ADD      r2, r2, r1
	ADD      r2, #0x40
	LDRB     r4, [r2]
	LDRB     r2, [r2, #1]
	LDR      r1, [r1, #0x60]
	ADD      r3, r3, r4
	ADD      r1, r1, r2
	SUB      r1, #0x20
	STR      r1, [r0, #4]
	STR      r3, [r0]
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x50]
	ADD      r6, r1, #0
	CMP      r0, #0
	SUB      sp, #0x24
	BNE      |sub_0800B386|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
