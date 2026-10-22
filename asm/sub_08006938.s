	CODE16
|sub_08006938|
|unk_08006938|
		SUB r0, r2, r7
		STR r0, [sp, #4]
		BNE      |loc_08006976|
		MOV r1, #0xa
		ADD r0, r5, #1
		BL       |sub_08046E40|
		LDR r0, [r6, #0x28]
		ADD r5, r0, r5
		MOV r7, #0
|loc_0800694C|
		MOV r0, #0xa
		STRB r0, [r5]
		MOV r1, #3
		ADD r0, r5, #1
		LDR r2, [r4, #0x18]
		BL       |sub_08046E40|
		LDR r0, [r4, #0x18]
		MOV r1, #0x68
		ADD r0, r0, r5
		STRB r1, [r0, #1]
		LDR r0, [r6, #0x28]
		ADD r7, #1
		ADD r5, r0, r5
		CMP r7, #3
		BLT      |loc_0800694C|
		ADD r0, r5, #1
		LDR r2, [r4, #0x18]
		BL       |sub_08046E40|
		B        |inc_0x0158_0x143f2| + 0x67dc
|loc_08006976|
		ADD r2, r7, #0
		MOV r1, #0xa
		ADD r0, r5, #1
		BL       |sub_08046E40|
		ADD r0, r5, r7
		ADD r0, #1
		MOV r1, #1
		LDR r2, [sp, #4]
		BL       |sub_08046E40|
		LDR r0, [r6, #0x28]
		LDR r2, [sp, #4]
		ADD r5, r0, r5
		MOV r0, #0
		SUB r2, #1
		STR r2, [sp, #8]
		STR r0, [sp]
|loc_0800699A|
		MOV r0, #0xa
		STRB r0, [r5]
		ADD r2, r7, #0
		MOV r1, #3
		ADD r0, r5, #1
		BL       |sub_08046E40|
		MOV r1, #0x68
		ADD r0, r5, r7
		STRB r1, [r0, #1]
		ADD r0, #2
		MOV r1, #0x70
		LDR r2, [sp, #8]
		BL       |sub_08046E40|
		LDR r0, [r4, #0x18]
		MOV r1, #1
		ADD r0, r0, r5
		STRB r1, [r0, #1]
		LDR r0, [r6, #0x28]
		ADD r5, r0, r5
		LDR r0, [sp]
		ADD r0, r0, r1
		STR r0, [sp]
		CMP r0, #3
		BLT      |loc_0800699A|
		ADD r2, r7, #0
		MOV r1, #0x68
		ADD r0, r5, #1
		BL       |sub_08046E40|
		ADD r0, r5, r7
		ADD r0, #1
		MOV r1, #0x73
		LDR r2, [sp, #4]
		BL       |sub_08046E40|
		B        |inc_0x0158_0x143f2| + 0x67dc
