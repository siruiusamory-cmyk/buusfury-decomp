	CODE16
|loc_0800E97E|
	PUSH     {r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	SUB      sp, #0x1c
	ADD      r0, sp, #0xc
	BL       |Object_GetPoints|
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	ADD      r4, #0xff
	ADD      r0, r0, r1
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0x10]
	ADD      r4, #0xc1
	SUB      r0, #2
	STR      r0, [sp, #8]
	LDR      r0, [pc, #0x194]
	LDR      r0, [r0, #4]
	LDR      r1, [r4, #0x1c]
	SUB      r1, r0, r1
	CMP      r1, #8
	BGE      |sub_0800E9C6|
	LDR      r1, [r4, #0x20]
	CMP      r1, #0
	BEQ      |sub_0800E9C6|
	ADD      r0, r1, #0
	LDR      r1, [r1, #0x14]
	LDR      r2, [r5]
	ADD      r2, r1, r2
	STR      r2, [r0, #0x14]
	BL       |loc_0800AB54|
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
