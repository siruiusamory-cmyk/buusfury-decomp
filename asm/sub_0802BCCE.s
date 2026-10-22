	CODE16
|sub_0802BCCE|
	MOV      r3, #0x34
	LDR      r1, [pc, #0x74]
	MUL      r0, r3
	ADD      r5, r0, r1
	ADD      r5, #0xc
	ADD      r1, r4, #0
	ADD      r0, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	ADD      r2, sp, #4
	ADD      r0, r0, r1
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0x10]
	ADD      r1, r5, #0
	STR      r0, [sp, #8]
	MOV      r0, #0
	BL       |loc_0802BD4C|
	ADD      r1, r0, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_0802BD04|
|unk_0802BD04|
		PUSH {r3, lr}
		LDR r2, [r0, #8]
		ADD r2, #1
		STR r2, [r0, #8]
		CMP r2, #0x3c
		BLT      |sub_0802BD32|
		LDR r1, [r1, #4]
		LDR r0, [r0, #0x10]
		CMP r0, #0
		BEQ      |sub_0802BD20|
		ADD r0, r1, #0
		BL       |inc_0x0158_0x143f2| + 0xf400
		B        |inc_0x2bb4c_0x2d1c0| + 0x1e2
