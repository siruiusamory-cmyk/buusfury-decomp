	CODE16
|sub_08006C3E|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08006C68|
	ADD      r6, r5, #4
|loc_08006C4C|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #0xd
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08006C4C|
|loc_08006C68|
	LDR      r0, [pc, #0xec]
	MOV      r1, #0xd
	LDR      r0, [r0, #4]
	BL       |inc_0x153f2_0x1a3f2| + 0x3fbc
	POP      {r4, r5, r6, pc}
|sub_08006C74|
|unk_08006C74|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [r0, #4]
		MOV r4, #0
		CMP r0, #0
		BLE      |inc_0x0158_0x143f2| + 0x6b6c
		LDR r0, [pc, #0xd4]
		LDR r7, [r0]
		ADD r7, #4
		STR r7, [sp]
		ADD r6, r5, #4
