	CODE16
|sub_0802214C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #0xd5
	ADD      r6, r0, #0
	LDR      r0, [r5]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08022174|
	LDR      r7, [pc, #0x17c]
|loc_08022160|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r1, [r0, #4]
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r5]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08022160|
|loc_08022174|
	ADD      r0, r6, #0
	BEQ      |loc_08022184|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08022184|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08022186|
|unk_08022186|
		PUSH {r4, r5, r6, r7, lr}
|loc_08022188|
|unk_08022188|
		ADD r4, r0, #0
		ADD r5, r4, #0
		ADD r5, #0xff
		LDR r0, [r0, #4]
		ADD r5, #0xd5
		CMP r0, #0
		SUB sp, #0x1c
		BEQ      |loc_0802227C|
		LDR r0, [r4, #8]
		ADD r2, sp, #0x14
		LDR r1, [r0, #0x2c]
		LDR r0, [r0, #0x30]
		STR r1, [sp, #0x14]
		STR r0, [sp, #0x18]
		LDR r3, [r4, #0xc]
		MOV r0, #0
		CMP r3, #0
		MOV ip, r3
		BLE      |loc_0802227C|
		ADD r6, r4, #0
		ADD r6, #0xc
		LDR r1, [r2]
		MOV lr, r6
