	CODE16
|sub_0803528C|
|unk_0803528C|
		LDRH r0, [r4, #0x12]
		LDR r5, [sp, #0x44]
		ADD r5, #4
		ADD r7, r5, #4
		CMP r0, #0
		BNE      |loc_08035320|
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		ADD r1, sp, #0xc
		ADD r0, sp, #0x1c
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r1, r4, #0
		ADD r0, sp, #0x24
		BL       |sub_0800FDFA|
		ADD r1, sp, #0x24
		ADD r0, sp, #0x34
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x34]
		LDR r2, [sp, #0x38]
		SUB r0, r0, r1
		LDR r1, [sp, #0x20]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #8]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		BGE      |loc_080352D2|
		NEG r0, r2
|loc_080352D2|
		ADD r1, r0, #0
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGE      |loc_080352DC|
		NEG r0, r0
|loc_080352DC|
		STR r0, [sp, #0x38]
		ADD r0, r1, #0
		STR r1, [sp, #0x34]
		LDR r1, [sp, #0x38]
		MOV r2, #0
		STR r2, [r5]
		STR r2, [r7]
		CMP r0, r1
		LDR r3, [pc, #0x2dc]
		BLE      |loc_0803532A|
		CMP r1, #8
		BGE      |loc_08035312|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		LDR r1, [sp, #0x3c]
		MOV r0, #3
		CMP r1, #0
		BGT      |loc_0803530C|
		MOV r0, #2
|loc_0803530C|
		STRB r0, [r4, #0x10]
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0xc8
|loc_08035312|
		ADD r1, sp, #0x40
		LDMIA r1!, {r0, r1}
		ADD r1, #8
		CMP r0, #0
		BLE      |loc_08035322|
		STRB r2, [r4, #0x10]
		STR r6, [r1]
|loc_08035320|
		B        |loc_08035360|
|loc_08035322|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		STR r3, [r1]
		B        |loc_08035360|
|loc_0803532A|
		CMP r0, #8
		BGE      |loc_0803534C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		LDR r1, [sp, #0x40]
		MOV r0, #1
		CMP r1, #0
		BLE      |loc_08035346|
		MOV r0, #0
|loc_08035346|
		STRB r0, [r4, #0x10]
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0xc8
|loc_0803534C|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BLE      |loc_0803535A|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		STR r6, [r5]
		B        |loc_08035360|
|loc_0803535A|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		STR r3, [r5]
|loc_08035360|
		LDRH r0, [r4, #0x12]
		CMP r0, #0x80
		BLS      |loc_080353CC|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		ADD r6, r4, #0
		ADD r6, #0xff
		ADD r6, #0xa1
		LDR r0, [r6]
		LDR r1, [r5]
		ADD r5, r6, #4
		ADD r0, r0, r1
		LDR r1, [r6, #4]
		LDR r2, [r7]
		STR r0, [sp, #0x2c]
		ADD r1, r1, r2
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x38]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x34]
		STR r0, [sp, #0x3c]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x3c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_080353BE|
		LDR r0, [sp, #0x3c]
		STR r0, [r6]
		LDR r0, [sp, #0x40]
		STR r0, [r5]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		B        |loc_080353CC|
|loc_080353BE|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_080353CC|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0xc8
