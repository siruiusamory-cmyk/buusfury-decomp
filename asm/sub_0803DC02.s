	CODE16
|sub_0803DC02|
|unk_0803DC02|
		LDR r1, [r7]
		LDMIA r1!, {r0}
		STR r1, [r7]
		LDRB r1, [r0]
		CMP r1, #0
		BEQ      |loc_0803DC80|
|loc_0803DC0E|
		LDRB r1, [r0]
		ADD r0, #1
		STRH r1, [r4]
		LDRB r1, [r0]
		ADD r4, #2
		CMP r1, #0
		BNE      |loc_0803DC0E|
		B        |loc_0803DC80|
|loc_0803DC1E|
|unk_0803DC1E|
		MOV r6, #0
		STR r6, [sp]
		LDR r1, [r7]
		LDMIA r1!, {r0}
		STR r1, [r7]
		CMP r0, #0
		BGE      |loc_0803DC32|
		NEG r0, r0
		MOV r1, #1
		STR r1, [sp]
|loc_0803DC32|
		BL       |sub_0805311C|
		ADD r0, #0x30
		ADD r2, r0, #0
		ADD r0, r6, #0
		ADD r3, sp, #4
		STRB r2, [r3, r0]
		ADD r6, #1
		ADD r0, r1, #0
		BNE      |loc_0803DC32|
		LDR r0, [sp]
		CMP r0, #0
		BEQ      |loc_0803DC56|
		MOV r1, #0x2d
		ADD r0, r6, #0
		ADD r2, sp, #4
		STRB r1, [r2, r0]
		ADD r6, #1
|loc_0803DC56|
		LDR r0, [sp, #0x18]
		SUB r0, r0, r6
		CMP r0, #0
		BLE      |loc_0803DC6A|
|loc_0803DC5E|
		LDR r1, [sp, #0x14]
		SUB r0, #1
		STRH r1, [r4]
		ADD r4, #2
		CMP r0, #0
		BGT      |loc_0803DC5E|
|loc_0803DC6A|
		CMP r6, #0
		BEQ      |loc_0803DC80|
		B        |inc_0x03d784_0x041118| + 0x4f0
|loc_0803DC70|
|unk_0803DC70|
		B        |loc_0803DC90|
|loc_0803DC72|
|unk_0803DC72|
		B        |inc_0x03d784_0x041118| + 0x4fe
