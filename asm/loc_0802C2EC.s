	CODE16
|loc_0802C2EC|
|unk_0802C2EC|
		STR r1, [sp, #0xc]
		ADD r0, r0, r2
		STR r0, [sp, #0x10]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #0x24]
		STR r0, [sp, #0x28]
		MOV r2, #0x37
		STR r5, [sp, #4]
		STR r1, [sp, #0xc]
		STR r0, [sp, #0x10]
		ADD r3, sp, #0x24
		ADD r1, r3, #0
		MOV r0, #0
		MOV r5, #4
		STR r2, [sp, #8]
		LDR r2, [pc, #0x38]
		ADD r3, r5, #0
		STR r7, [sp]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r6]
		BL       |List_Append|
		B        |sub_0802C328|
|loc_0802C320|
		ADD r5, #1
		CMP r5, #0x10
		BGE      |sub_0802C328|
		B        |loc_0802C1FA|
