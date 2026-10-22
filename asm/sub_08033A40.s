	CODE16
|sub_08033A40|
|unk_08033A40|
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BGT      |loc_08033A5C|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033A5C|
		LDR r1, [pc, #0xd8]
		LDR r0, [r4, #0x14]
		CMP r0, r1
		BEQ      |loc_08033A68|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033A68|
		LDR r0, [pc, #0xd0]
		LDR r2, [pc, #0xd8]
		SUB r0, #4
		LDR r0, [r0]
		LDRH r1, [r0, #4]
		MOV r0, #0xf3
		AND r1, r0
		MOV r0, #0
		CMP r1, #0
		LDR r1, [r2, #4]
		BEQ      |loc_08033A9C|
		STR r1, [r5, #4]
		LDR r1, [r5, #8]
		ADD r1, #1
		STR r1, [r5, #8]
		CMP r1, #8
		BLE      |loc_08033AA6|
		LDR r0, [r7]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033A9C|
		LDR r3, [r5, #4]
		SUB r1, r1, r3
		CMP r1, #0xa
		BLE      |loc_08033AA6|
		STR r0, [r5, #8]
|loc_08033AA6|
		LDR r1, [r2, #4]
		LSL r1, r1, #0x1c
		BNE      |loc_08033AD6|
		MOV r2, #0xff
		ADD r2, #0xb3
		LDRH r2, [r2, r6]
		STR r0, [sp, #0x10]
		ADD r0, r4, #0
		LSL r2, r2, #0xa
		STR r2, [sp, #0x18]
		LDR r2, [r4]
		MOV r1, sp
		LDR r3, [r2, #0x5c]
		ADD r5, sp, #0x18
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x60]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |loc_08046AA4|
|loc_08033AD6|
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BGT      |loc_08033AF2|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033AF2|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x87c
