	CODE16
|sub_08019BE4|
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LDR      r1, [pc, #0x118]
	PUSH     {r4}
	LDR      r1, [r1, #4]
	LDR      r2, [r0, #0x28]
	ADD      r1, #0x18
	LDR      r3, [r1, #8]
	SUB      sp, #8
	CMP      r2, r3
	BGE      |sub_08019C40|
	LDR      r2, [r1]
	LDR      r3, [r0, #0x30]
	CMP      r2, r3
	BGE      |sub_08019C40|
	LDR      r2, [r0, #0x2c]
	LDR      r3, [r1, #0xc]
	CMP      r2, r3
	BGE      |sub_08019C40|
	LDR      r2, [r1, #4]
	LDR      r3, [r0, #0x34]
	CMP      r2, r3
	BGE      |sub_08019C40|
	ADD      r2, r0, #0
	LDR      r3, [r0, #0x28]
	LDR      r4, [r1]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x38
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4}
	BX       lr
