	CODE16
|sub_0803A6D8|
|unk_0803A6D8|
		MOV r0, #0
		STRB r0, [r4, #0x10]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [sp, #4]
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		ADD r1, r0, #0
		LDR r0, [sp, #0xc]
		ADD r1, #0x20
		SUB r0, #0x10
		STR r0, [sp, #4]
		STR r0, [sp, #0x14]
		ADD r2, r4, #0
		STR r1, [sp]
		STR r1, [sp, #0x10]
		MOV r3, #2
		MOV r0, #0
		ADD r1, sp, #0x10
		BL       |inc_0x351c0_0x3d4d0| + 0x1de2
		ADD r1, r0, #0
		STR r0, [r6, #4]
		LDR r0, [r5]
		BL       |List_Append|
		B        |inc_0x351c0_0x3d4d0| + 0x5514
|loc_0803A71E|
|unk_0803A71E|
		CMP r2, r0
		BLE      |loc_0803A726|
		STRB r0, [r4, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0x5514
|loc_0803A726|
		MOV r0, #0xff
		ADD r0, #0x2d
		CMP r1, r0
		BLS      |inc_0x351c0_0x3d4d0| + 0x5514
		ADD r0, r4, #0
		BL       |sub_0800EE78|
		B        |inc_0x351c0_0x3d4d0| + 0x5514
