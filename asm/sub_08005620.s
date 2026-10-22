	CODE16
|sub_08005620|
|unk_08005620|
		LDR r1, [sp]
		LDR r0, [r1, #0x18]
		LDR r1, [pc, #0xd4]
		LSL r0, r0, #2
		LDR r1, [r1, r0]
		ADD r0, r4, #0
		BL       |loc_0803DADA|
		B        |inc_0x0158_0x143f2| + 0x54c6
		PUSH {r4, r5, r6, lr}
		ADD r4, r0, #0
		ADD r4, #0xff
		ADD r4, #1
		ADD r5, r0, #0
		LDR r0, [r4, #0xc]
		LDR r1, [r4, #0x28]
		SUB sp, #0x38
		CMP r0, r1
		BGE      |loc_08005648|
		STR r0, [r4, #0x28]
|loc_08005648|
		LDR r1, [r4, #0x28]
		ADD r1, #1
		CMP r0, r1
		BLE      |loc_08005654|
		SUB r1, r0, #1
		STR r1, [r4, #0x28]
|loc_08005654|
		MOV r1, #5
		LSL r1, r1, #7
		ADD r2, r5, r1
		LDR r1, [r2, #0x2c]
		LDR r3, [r4, #0x20]
		CMP r3, #0
		BEQ      |loc_0800566A|
		CMP r0, #0
		BEQ      |loc_0800566A|
		MOV r0, #1
		B        |loc_0800566C|
|loc_0800566A|
		MOV r0, #0
|loc_0800566C|
		STR r0, [r1, #8]
		LDR r0, [r2, #0x30]
		LDR r1, [r4, #0x20]
		CMP r1, #0
		BEQ      |sub_08005680|
		LDR r1, [r4, #0xc]
		CMP r1, #2
		BEQ      |sub_08005680|
		MOV r1, #1
		B        |inc_0x0158_0x143f2| + 0x552a
