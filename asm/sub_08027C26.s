	CODE16
|sub_08027C26|
	LSL      r0, r0, #0
	SUB      r0, r2, r4
	LSL      r0, r0, #0xc
	DCW      0xea40,0x0874
	PUSH     {r4, r5, lr}
	SUB      sp, #0x2c
	ADD      r4, r0, #0
	ADD      r0, sp, #0x1c
	LDR      r1, [r1, #4]
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r5, [pc, #0x78]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x115da
	LDR      r0, [sp, #0x1c]
	LDR      r1, [sp, #0x24]
	LDR      r2, [sp, #0x28]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x20]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r4, #8]
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x10]
	LDR      r2, [r4, #0xc]
	STR      r0, [sp, #4]
	ADD      r1, r1, r2
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x18]
	MOV      r2, #0x37
	STR      r0, [sp, #0x14]
	MOV      r0, #0
	ADD      r1, sp, #0x14
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x2c
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r4, [pc, #0x20]
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r1, r5, #0
	ADD      r1, #8
	MOV      r2, #0x37
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	DCW      0xea44,0x0874
|loc_08027CBC|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08027CD8|
	MOV      r0, #0x54
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08027CD8|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
