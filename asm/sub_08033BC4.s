	CODE16
|sub_08033BC4|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x19c]
	ADD      r4, r1, #0
	LDR      r5, [r0]
	SUB      sp, #0x6c
	CMP      r5, #0
	BEQ      |sub_08033CB8|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r5]
	CMP      r0, #0
	BEQ      |sub_08033CB8|
	ADD      r1, r5, #0
	ADD      r0, sp, #0x5c
	BL       |inc_0x0158_0x143f2| + 0xfd20
	ADD      r1, r4, #0
	ADD      r0, sp, #0x4c
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x4c]
	LDR      r1, [sp, #0x54]
	LDR      r2, [sp, #0x58]
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x50]
	STR      r0, [sp, #0x3c]
	ADD      r1, r1, r2
	ASR      r0, r0, #1
	ASR      r3, r1, #1
	STR      r0, [sp, #0x44]
	STR      r0, [sp, #0x3c]
	STR      r1, [sp, #0x40]
	LDR      r1, [sp, #0x64]
	LDR      r0, [sp, #0x5c]
	STR      r3, [sp, #0x40]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x60]
	STR      r3, [sp, #0x48]
	LDR      r2, [sp, #0x68]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	STR      r1, [sp]
	STR      r1, [sp, #8]
	LDR      r1, [sp, #0x44]
	LDR      r2, [sp, #0x48]
	SUB      r0, r0, r1
	LDR      r1, [sp, #0xc]
	STR      r0, [sp]
	SUB      r6, r1, r2
	ADD      r1, r0, #0
	CMP      r0, #0
	STR      r6, [sp, #4]
	BGE      |loc_08033C3C|
|unk_08033C3A|
	INCBIN	baserom.gba_0x33c3a_0x33c3c.extracted
