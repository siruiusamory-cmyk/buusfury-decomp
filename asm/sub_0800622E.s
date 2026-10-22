	CODE16
|sub_0800622E|
	MOV      r1, #2
	STRB     r1, [r0, #3]
	LDR      r1, [pc, #0x54]
	LDR      r1, [r1, #8]
	STR      r1, [r0, #0xc]
	LDR      r3, [r2, #0x20]
	LDR      r4, [r2, #0x24]
	STR      r3, [r0, #4]
	STR      r4, [r0, #8]
	LDR      r1, [r2, #0x1c]
	BL       |inc_0x03d784_0x041118| + 0x356
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r5, r1, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0xc]
	LDR      r1, [r4, #8]
	CMP      r0, r1
	BEQ      |sub_08006260|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
