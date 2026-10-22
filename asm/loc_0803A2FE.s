	CODE16
|loc_0803A2FE|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x70]
	SUB      sp, #0x28
	LDR      r0, [r0]
	LDR      r1, [pc, #0x8c]
	MOV      r2, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STR      r2, [sp, #0x14]
	STR      r1, [sp, #0x10]
	LDMIA    r0!, {r2}
	LDR      r0, [r0]
	ADD      r1, r2, r1
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	STR      r1, [sp, #8]
	LDR      r1, [sp, #0xc]
	STR      r0, [sp, #0x18]
	STR      r1, [sp, #0x1c]
	STR      r1, [sp, #0x24]
	LDR      r1, [pc, #0x50]
	STR      r0, [sp, #0x20]
	MOV      r2, #0x20
	ADD      r1, #8
	MOV      r0, sp
	MOV      r4, sp
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #0x20]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xc]
	LDR      r0, [sp, #0x24]
	LDR      r1, [pc, #0x40]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0xe]
	LDR      r0, [sp, #8]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x14]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r4, #0
	ADD      sp, #0x28
	POP      {r4, pc}
|loc_0803A36E|
	DCW      0x0000
	DCW      0x8098,0x086b,0x1c34,0x0300,0xb048,0x0877,0x92a8,0x0831
	DCW      0x05c4,0x0000,0x1274,0x0871,0xc338,0x0804,0xd738,0x0804
	DCW      0xc194,0x0804,0xec00,0xffff
