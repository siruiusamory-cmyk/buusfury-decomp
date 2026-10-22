	CODE16
|sub_0803101A|
|unk_0803101A|
		MOV r0, #1
		LSL r0, r0, #9
		ADD r2, r5, r0
		LDR r0, [r2, #4]
		ADD r6, r4, #4
		CMP r0, #0
		BEQ      |loc_08031090|
		MOV r3, #0x80
		BIC r0, r3
		LSL r3, r3, #3
		CMP r0, #0
		BEQ      |loc_08031056|
		CMP r0, #1
		BEQ      |loc_0803104E|
		CMP r0, #2
		BEQ      |loc_08031046|
		CMP r0, #3
		BNE      |loc_0803105C|
		LDR r0, [r4, #4]
		ADD r0, r0, r3
		STR r0, [r4, #4]
		B        |loc_0803105C|
|loc_08031046|
		LDR r0, [r4, #4]
		SUB r0, r0, r3
		STR r0, [r4, #4]
		B        |loc_0803105C|
|loc_0803104E|
		LDR r0, [r4, #8]
		SUB r0, r0, r3
		STR r0, [r4, #8]
		B        |loc_0803105C|
|loc_08031056|
		LDR r0, [r4, #8]
		ADD r0, r0, r3
		STR r0, [r4, #8]
|loc_0803105C|
		LDR r3, [r4, #4]
		CMP r3, #0x80
		BLE      |loc_08031068|
		MOV r0, #0x80
		STR r0, [r6]
		B        |loc_0803108C|
|loc_08031068|
		MOV r0, #0x7f
		MVN r0, r0
		ADD r7, r0, #0
		CMP r3, r7
		BGE      |loc_08031076|
		STR r0, [r6]
		B        |loc_0803108C|
|loc_08031076|
		ADD r3, r4, #0
		LDR r7, [r4, #8]
		ADD r3, #8
		CMP r7, #0x80
		BLE      |loc_08031086|
		MOV r0, #0x80
		STR r0, [r3]
		B        |loc_0803108C|
|loc_08031086|
		CMP r7, r0
		BGE      |loc_0803108C|
		STR r0, [r3]
|loc_0803108C|
		MOV r0, #0
		STR r0, [r2, #4]
|loc_08031090|
		ADD r0, sp, #0xc
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x24
		ADD r1, r5, #0
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		ADD r1, r0, r1
		LDR r0, [sp, #0x28]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x38]
		ASR r1, r1, #1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #4]
		STR r1, [sp, #0x34]
		SUB r1, r0, r1
		LDR r0, [sp, #0x20]
		LDR r2, [sp, #0x38]
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		SUB r0, r0, r2
		LDR r1, [pc, #0x168]
		STR r0, [sp, #8]
		STR r0, [sp, #0x40]
		LDR r0, [r1, #4]
		ADD r7, r1, #0
		CMP r0, #0
		BNE      |loc_080310FE|
		MOV r0, #1
		STR r0, [r1, #4]
		LDR r0, [pc, #0x15c]
		BL       |sub_08054A64|
		STR r0, [r7]
|loc_080310FE|
		LDR r1, [sp, #0x3c]
		CMP r1, #0
		BLE      |loc_08031112|
		LDR r0, [r4, #4]
		CMP r0, #0x80
		BGE      |loc_08031122|
		LDR r1, [r7]
		ADD r0, r0, r1
		STR r0, [r4, #4]
		B        |loc_08031122|
|loc_08031112|
		MOV r1, #0x7f
		LDR r0, [r4, #4]
		MVN r1, r1
		CMP r0, r1
		BLE      |loc_08031122|
		LDR r1, [r7]
		SUB r0, r0, r1
		STR r0, [r4, #4]
|loc_08031122|
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BLE      |loc_08031136|
		LDR r0, [r4, #8]
		CMP r0, #0x80
		BGE      |loc_08031146|
		LDR r1, [r7]
		ADD r0, r0, r1
		STR r0, [r4, #8]
		B        |loc_08031146|
|loc_08031136|
		MOV r1, #0x7f
		LDR r0, [r4, #8]
		MVN r1, r1
		CMP r0, r1
		BLE      |loc_08031146|
		LDR r1, [r7]
		SUB r0, r0, r1
		STR r0, [r4, #8]
|loc_08031146|
		LDR r0, [r4, #4]
		CMP r0, #0
		BLT      |loc_08031150|
		ADD r1, r0, #0
		B        |loc_08031152|
|loc_08031150|
		NEG r1, r0
|loc_08031152|
		LDR r2, [r4, #8]
		CMP r2, #0
		BLT      |loc_0803115C|
		ADD r3, r2, #0
		B        |loc_0803115E|
|loc_0803115C|
		NEG r3, r2
|loc_0803115E|
		CMP r1, r3
		BLE      |loc_08031170|
		CMP r0, #0
		BLE      |loc_0803116A|
		MOV r0, #3
		B        |loc_0803116C|
|loc_0803116A|
		MOV r0, #2
|loc_0803116C|
		STRB r0, [r5, #0x10]
		B        |loc_08031180|
|loc_08031170|
		CMP r2, #0
		BLE      |loc_08031178|
		MOV r0, #1
		B        |loc_0803117A|
|loc_08031178|
		MOV r0, #0
|loc_0803117A|
		MOV r1, #1
		SUB r0, r1, r0
		STRB r0, [r5, #0x10]
|loc_08031180|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		ADD r4, r5, #0
		ADD r4, #0xff
		ADD r4, #0xa1
		LDR r0, [r4]
		LDR r1, [r6]
		LDR r2, [r4, #4]
		ADD r0, r0, r1
		LDR r1, [r6, #4]
		STR r0, [sp, #0x24]
		ADD r1, r2, r1
		STR r1, [sp, #0x28]
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x38]
		STR r0, [sp, #0x2c]
		STR r0, [sp, #0x34]
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x54]
		ADD r7, r4, #4
		ADD r2, r2, r1
		ADD r1, sp, #0x34
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		DCW     0xD004
