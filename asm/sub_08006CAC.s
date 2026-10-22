	CODE16
|sub_08006CAC|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #0xe
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08006C8A|
	LDR      r0, [pc, #0x90]
	MOV      r1, #0xe
	LDR      r0, [r0, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	ADD      r0, r5, #0
	BEQ      |loc_08006CDE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08006CDE|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08006CE0|
|unk_08006CE0|
		PUSH {r4, r5, r6, r7, lr}
		ADD r6, r0, #0
		LDR r0, [r0, #4]
		MOV r5, #0
		MOV r4, #0
		CMP r0, #0
		SUB sp, #0xc
		BLE      |inc_0x0158_0x143f2| + 0x6be2
		LDR r0, [pc, #0x64]
		LDR r7, [r0]
		ADD r7, #4
		ADD r1, r6, #4
		STR r1, [sp, #4]
		STR r7, [sp, #8]
