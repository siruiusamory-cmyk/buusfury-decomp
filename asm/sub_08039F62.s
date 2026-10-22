	CODE16
|sub_08039F62|
|unk_08039F62|
		MOV r1, #0xff
		ADD r1, #0xa9
		ADD r2, r1, #0
		LDR r2, [r2, r0]
		ADD r0, #0xff
		ADD r0, #0xa1
		STR r2, [r1, r7]
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
		LDR r1, [r6, #4]
		SUB r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r6, #8]
		STR r0, [sp]
		SUB r1, r1, r2
		STR r1, [sp, #4]
		ADD r5, r1, #0
		ADD r1, r0, #0
		ADD r4, r0, #0
		MUL r0, r1
		ADD r1, r5, #0
		MUL r1, r5
		ADD r0, r0, r1
		BL       |sub_0803FAF6|
		STR r0, [sp, #0xc]
		LDR r0, [r6, #0xc]
		ADD r1, r4, #0
		MUL r1, r0
		ADD r2, r5, #0
		MUL r2, r0
		STR r2, [sp, #0x10]
		STR r2, [sp, #8]
		LDR r0, [sp, #0xc]
		STR r1, [sp, #4]
		BL       |sub_08046E58|
		STR r0, [sp]
		ADD r1, sp, #0xc
		LDMIA r1!, {r0, r1}
		BL       |sub_08046E58|
		LDR r1, [sp]
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		LDR r2, [r6, #4]
		ADD r0, r2, r0
		LDR r2, [r6, #8]
		STR r0, [sp, #4]
		ADD r1, r2, r1
		STR r1, [sp, #8]
		ADD r1, r0, #0
		ADD r0, r7, #0
		ADD r0, #0xff
		LDR r2, [sp, #8]
		ADD r0, #0xa1
		LSL r1, r1, #8
		STMIA r0!, {r1}
		LSL r2, r2, #8
		ADD r1, r4, #0
		CMP r4, #0
		STR r2, [r0]
		BGE      |loc_08039FF6|
		NEG r1, r1
|loc_08039FF6|
		ADD r0, r5, #0
		CMP r5, #0
		BGE      |loc_08039FFE|
		NEG r0, r0
|loc_08039FFE|
		ADD r2, r7, #0
		ADD r2, #0xff
		ADD r2, #0x81
		CMP r1, r0
		BLE      |loc_0803A02C|
		CMP r4, #0
		BLE      |loc_0803A01C|
		CMP r5, #0
		BLE      |loc_0803A016|
		MOV r0, #0x50
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A016|
		MOV r0, #0x30
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A01C|
		CMP r5, #0
		BLE      |loc_0803A026|
		MOV r0, #0xb0
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A026|
		MOV r0, #0xd0
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A02C|
		CMP r5, #0
		BLE      |loc_0803A040|
		CMP r4, #0
		BLE      |loc_0803A03A|
		MOV r0, #0x70
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A03A|
		MOV r0, #0x90
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A040|
		CMP r4, #0
		BLE      |loc_0803A04A|
		MOV r0, #0x10
		STR r0, [r2, #0x2c]
		B        |loc_0803A04E|
|loc_0803A04A|
		MOV r0, #0xf0
		STR r0, [r2, #0x2c]
|loc_0803A04E|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x4d9e
