	CODE16
|sub_0802A412|
|unk_0802A412|
		CMP r1, #0
		BEQ      |loc_0802A4C8|
		LDR r0, [r4, #0x40]
		LDR r1, [r4, #0x38]
		LDR r2, [r4, #0x3c]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r1, [sp, #0x3c]
		ADD r1, r2, #0
		STR r2, [sp, #0x40]
		LDR r2, [r4, #0x20]
		ADD r3, sp, #0x20
		ADD r0, r2, r0
		LDR r2, [r4, #0x24]
		STR r0, [sp, #0x3c]
		ADD r1, r2, r1
		STR r1, [sp, #0x40]
		STR r1, [sp, #0x48]
		STR r0, [sp, #0x44]
		LDR r0, [r4, #0x4c]
		MOV r5, #1
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x44]
		ADD r2, sp, #0x44
		STRB r0, [r3, #4]
		LDR r0, [pc, #0x15c]
		ADD r3, sp, #0
		STR r0, [sp, #0x2c]
		LSL r0, r5, #0xa
		STR r0, [sp, #0x28]
		MOV r0, #0
		STRB r0, [r3, #0x10]
		STR r4, [sp, #0x40]
		LDR r0, [sp, #0x44]
		LDR r1, [r4, #0x20]
		ADD r3, r4, #0
		ADD r3, #0x20
		CMP r0, r1
		BGE      |loc_0802A466|
		ADD r0, r2, #0
		B        |loc_0802A468|
|loc_0802A466|
		ADD r0, r3, #0
|loc_0802A468|
		LDR r0, [r0]
		LDR r6, [sp, #0x48]
		SUB r0, #4
		STR r0, [sp, #0x14]
		ADD r0, r4, #0
		LDR r7, [r4, #0x24]
		ADD r0, #0x24
		ADD r1, r2, #4
		CMP r6, r7
		BGE      |loc_0802A480|
		ADD r6, r1, #0
		B        |loc_0802A482|
|loc_0802A480|
		ADD r6, r0, #0
|loc_0802A482|
		LDR r6, [r6]
		SUB r6, #4
		STR r6, [sp, #0x18]
		LDR r6, [sp, #0x44]
		LDR r7, [r3]
		CMP r6, r7
		BLE      |loc_0802A492|
		ADD r3, r2, #0
|loc_0802A492|
		LDR r3, [r3]
		LDR r2, [sp, #0x48]
		ADD r3, #4
		STR r3, [sp, #0x1c]
		LDR r3, [r0]
		CMP r2, r3
		BLE      |loc_0802A4A2|
		ADD r0, r1, #0
|loc_0802A4A2|
		LDR r0, [r0]
		LDR r6, [pc, #0xdc]
		ADD r0, #4
		STR r0, [sp, #0x20]
		LDR r1, [r6, #8]
		ADD r7, sp, #0x10
		ADD r0, r7, #4
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		DCW     0xD03E
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6, #4]
		BL       |loc_08011C0C|
		DCW     0xE000
|loc_0802A4C8|
|unk_0802A4C8|
		B        |loc_0802A53C|
		CMP r0, #0
		BEQ      |loc_0802A508|
		LDR r0, [r6, #4]
		BL       |loc_080116FC|
		MOV r6, #1
		LSL r6, r6, #0xa
		CMP r0, r6
		BLT      |loc_0802A504|
		LSL r7, r6, #2
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		MOV r2, #0x37
		ADD r0, r0, r7
		STR r0, [sp]
		STR r2, [sp, #8]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0xb4]
		STR r6, [sp, #4]
		ADD r1, sp, #0x44
		BL       |loc_0802A81C|
		LDR r6, [pc, #0x88]
		ADD r1, r0, #0
		LDR r0, [r6, #4]
		BL       |List_Append|
|loc_0802A504|
		STRB r5, [r4, #0x10]
		B        |loc_0802A53C|
|loc_0802A508|
		LDR r0, [r4, #0x40]
		CMP r0, #0x30
		BGE      |loc_0802A514|
		ADD r0, #4
		STR r0, [r4, #0x40]
		B        |loc_0802A52C|
|loc_0802A514|
		LDR r0, [r4, #0x38]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #0xc]
		STR r0, [sp, #8]
		LDR r2, [r4, #0x20]
		ADD r0, r2, r0
		STR r0, [r4, #0x20]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
|loc_0802A52C|
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		CMP r0, #0xf0
		BLE      |loc_0802A53C|
		STRB r5, [r4, #0x10]
		B        |loc_0802A53C|
		STRB r5, [r4, #0x10]
