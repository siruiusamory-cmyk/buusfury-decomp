	CODE16
|sub_0800ABE6|
|unk_0800ABE6|
		LDR r0, [pc, #0x1ac]
		LDR r7, [pc, #0x190]
		STR r0, [r4]
		MOV r0, #0xff
		ADD r0, #1
		STRH r0, [r4, #0xe]
		ADD r1, r0, #0
		LDR r0, [r7]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0800AC12|
		MOV r1, #0xff
		ADD r1, #1
		LDR r0, [r7]
		BL       |sub_08011732|
		MOV r1, #0xff
		ADD r1, #1
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_0800AC12|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x180]
		STR r0, [r4]
		LDR r1, [sp, #0xc]
		ADD r0, r4, #0
		LDR r1, [r1]
		ADD r0, #0x20
		STR r1, [r4, #0x14]
		LDR r2, [sp, #0x10]
		STR r2, [r4, #0x18]
		STR r6, [r4, #0x1c]
		LDR r2, [r5]
		LDR r3, [r5, #4]
		SUB r2, #0x10
		LSL r2, r2, #3
		STR r2, [r4, #0x20]
		LSL r3, r3, #3
		STR r3, [r0, #4]
		ADD r0, r4, #0
		BL       |loc_0800AB54|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xaa8a
