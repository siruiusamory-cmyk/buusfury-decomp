	CODE16
|sub_08035704|
|unk_08035704|
		CMP r1, #0
		BEQ      |loc_08035700|
		LDR r0, [r4, #0x34]
		LDR r1, [r4, #0x2c]
		LDR r2, [r4, #0x30]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r1, [sp, #0x30]
		ADD r1, r2, #0
		STR r2, [sp, #0x34]
		LDR r2, [r4, #0x1c]
		ADD r3, sp, #0
		ADD r0, r2, r0
		LDR r2, [r4, #0x20]
		STR r0, [sp, #0x30]
		ADD r1, r2, r1
		STR r1, [sp, #0x34]
		LDR r2, [sp, #0x34]
		ADD r1, r0, #0
		LDR r0, [r4, #0x40]
		ADD r5, sp, #4
		STR r0, [sp, #0x24]
		LDR r0, [r4, #0x38]
		STRB r0, [r3, #0x18]
		LDR r0, [pc, #0x164]
		MOV r3, #0
		STR r0, [sp, #0x20]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x1c]
		ADD r0, r3, #0
		ADD r3, sp, #0
		STRB r0, [r3, #4]
		ADD r0, r5, #4
		ADD r5, r2, #0
		ADD r3, r1, #0
		SUB r3, #8
		ADD r1, #8
		SUB r5, #8
		ADD r2, #8
		STR r4, [sp, #0x34]
		STR r2, [sp, #0x14]
		STR r5, [sp, #0xc]
		STR r1, [sp, #0x10]
		STR r3, [sp, #8]
		LDR r1, [r6, #4]
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		MOV r5, #1
		CMP r0, #0
		BEQ      |loc_08035792|
		ADD r2, sp, #4
		MOV r1, #0
		LDR r0, [r6]
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_08035782|
		STRB r5, [r4, #0x10]
		B        |loc_08035700|
|loc_08035782|
		LDR r0, [r4, #0x34]
		CMP r0, #0x34
		BGE      |loc_0803578E|
		ADD r0, #4
		STR r0, [r4, #0x34]
		B        |loc_08035700|
|loc_0803578E|
		STRB r5, [r4, #0x10]
		B        |loc_08035700|
|loc_08035792|
		STRB r5, [r4, #0x10]
		B        |loc_08035700|
