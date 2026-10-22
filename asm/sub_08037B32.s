	CODE16
|sub_08037B32|
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
|unk_08037B40|
	INCBIN	baserom.gba_0x37b40_0x37b42.extracted
	LSR      r6, r6, #1
	ADD      r2, #0x88
	LSL      r0, r0, #0xc
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
