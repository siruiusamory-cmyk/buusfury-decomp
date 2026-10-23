|sub_08037B48|
	EXPORT |sub_08037B48|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x68]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x20
	ADD      r0, sp, #0x10
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x10]
	ADD      r0, #6
	STR      r0, [sp, #0x10]
	LDR      r0, [sp, #0x18]
	SUB      r0, #6
	STR      r0, [sp, #0x18]
	MOV      r0, sp
	ADD      r1, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x10]
	LDR      r1, [sp, #8]
	CMP      r0, r1
	BGE      |sub_08037B92|
	LDR      r0, [sp]
	LDR      r1, [sp, #0x18]
	CMP      r0, r1
	BGE      |sub_08037B92|
	LDR      r0, [sp, #0x14]
	LDR      r1, [sp, #0xc]
	CMP      r0, r1
	BGE      |sub_08037B92|
	LDR      r0, [sp, #4]
	LDR      r1, [sp, #0x1c]
	CMP      r0, r1
	BGE      |sub_08037B92|
	MOV      r0, #1
	ADD      sp, #0x20
	POP      {r4, pc}
