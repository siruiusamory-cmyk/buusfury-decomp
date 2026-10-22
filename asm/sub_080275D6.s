	CODE16
|sub_080275D6|
|unk_080275D6|
		LDR r0, [r4, #0x18]
		SUB r0, #0x30
		STR r0, [r4, #0x18]
		B        |loc_0802758C|
|loc_080275DE|
|unk_080275DE|
		LDR r0, [r4, #0x18]
		ADD r0, #0x30
		STR r0, [r4, #0x18]
		B        |loc_0802758C|
|loc_080275E6|
|unk_080275E6|
		LDR r0, [r4, #0x18]
		ADD r0, #0x30
		STR r0, [r4, #0x18]
		B        |loc_0802758C|
|loc_080275EE|
|unk_080275EE|
		ADD r0, r4, #0
		ADD r0, #0x28
		LDR r1, [r6, #4]
		ADD r5, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0802760A|
		ADD r0, r4, #0
		BL       |sub_08027516|
		DCW     0xE7E3
|loc_0802760A|
		CMP r7, #0
		DCW     0xD0E1
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		DCW     0xD0DE
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x80]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r5}
		MOV r0, #0
		ADD r3, sp, #0
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6]
		BL       |List_CallMethod1|
		CMP r0, #0
		DCW     0xD0C5
		ADD r0, r4, #0
		BL       |sub_08027516|
		DCW     0xE7C1
