	CODE16
|sub_0802770C|
	PUSH     {r4, r5, lr}
	LDR      r1, [r0, #0x20]
	SUB      sp, #0x14
	ASR      r1, r1, #8
	STR      r1, [sp, #0xc]
	LDR      r1, [r0, #0x24]
	LDR      r4, [pc, #0x214]
	ASR      r1, r1, #8
	STR      r1, [sp, #0x10]
	ADD      r1, r0, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r1, #0x45
	LDR      r2, [pc, #0x208]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r5, [pc, #0x204]
	LDR      r0, [r4]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r5
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0802776A|
	MOV      r2, #0x38
	LSL      r0, r1, #3
	STR      r0, [sp]
	STR      r2, [sp, #8]
	STR      r1, [sp, #4]
	MOV      r3, #4
	MOV      r0, #0
	ADD      r1, sp, #0xc
	LDR      r2, [pc, #0x1dc]
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0802776A|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x48]
	SUB      sp, #0x34
	ADD      r0, #1
	STR      r0, [r4, #0x48]
	ADD      r6, r4, #0
	ADD      r6, #0x40
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1e
	ADD      r5, r6, #4
	CMP      r0, #0
	BNE      |loc_08027816|
	LDR      r0, [pc, #0x1a4]
	SUB      r0, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	CMP      r0, #0x40
	BLT      |loc_08027816|
	LDR      r1, [r6]
	LDR      r2, [r5]
	LSL      r1, r1, #0xb
	LSL      r2, r2, #0xb
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	ADD      r0, r4, #0
	ADD      r0, #0x20
	STR      r1, [sp, #0x14]
	STR      r1, [sp, #0x1c]
	STR      r2, [sp, #0x18]
	STR      r2, [sp, #0x20]
	LDR      r1, [r0]
	LDR      r2, [sp, #0x1c]
	LDR      r3, [r0, #4]
	SUB      r2, r1, r2
	LDR      r7, [sp, #0x20]
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x24]
	SUB      r3, r3, r7
	ASR      r2, r2, #8
	STR      r2, [sp, #0x2c]
	STR      r3, [sp, #0x18]
	STR      r3, [sp, #0x28]
	LDR      r2, [r6]
	LDR      r7, [r5]
	LSL      r2, r2, #0xb
	LSL      r3, r7, #0xb
	ASR      r3, r3, #8
	ASR      r2, r2, #8
	STR      r2, [sp, #0x14]
	STR      r2, [sp, #0x1c]
	STR      r3, [sp, #0x18]
	STR      r3, [sp, #0x20]
	ADD      r1, r0, #4
	LDR      r0, [r0]
	LDR      r1, [r1]
	SUB      r0, r0, r2
	SUB      r1, r1, r3
	STR      r0, [sp, #0x14]
	STR      r0, [sp, #0x24]
	ASR      r0, r1, #8
	STR      r1, [sp, #0x28]
	MOV      r2, #0x38
	STR      r2, [sp, #8]
	STR      r0, [sp, #0x30]
	STR      r1, [sp, #0x18]
	MOV      r1, #0x40
	LDR      r0, [pc, #0x148]
	LDR      r2, [pc, #0x130]
	STR      r1, [sp, #4]
	MOV      r3, #3
	STR      r0, [sp]
	ADD      r2, #0x30
	MOV      r0, #0
	ADD      r1, sp, #0x2c
	BL       |loc_0802A81C|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x120]
	SUB      r0, #0xc
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08027816|
	LDR      r0, [r4, #0x20]
	LDR      r1, [r6]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x20]
	LDR      r0, [r4, #0x24]
	LDR      r1, [r5]
	ADD      r0, r0, r1
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r6, [pc, #0x100]
	SUB      r6, #0xc
	LDR      r0, [r6, #8]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [r4, #0x30]
	CMP      r1, r2
	BGE      |loc_08027854|
	LDR      r1, [r4, #0x28]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_08027854|
	LDR      r1, [r0, #4]
	LDR      r2, [r4, #0x34]
	CMP      r1, r2
	BGE      |loc_08027854|
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BLT      |sub_08027860|
|loc_08027854|
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
