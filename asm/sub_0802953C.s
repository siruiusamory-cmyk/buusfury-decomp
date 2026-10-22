	CODE16
|sub_0802953C|
|unk_0802953C|
		LDR r1, [r2, #0x1c]
		LDRB r1, [r1]
		CMP r1, #1
		BNE      |loc_0802957A|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0802957A|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0802957A|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0802957A|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0802957A|
		MOV r1, #0x10
		STR r1, [r0, #0x4c]
		LDR r1, [pc, #0x64]
		STR r1, [r0, #0x54]
		ADD r0, #0x40
		MOV r1, #0
		STMIA r0!, {r1}
		STR r1, [r0]
		MOV r0, #1
		DCW     0xE7DF
|loc_0802957A|
|unk_0802957A|
		MOV r0, #0
		DCW     0xE7DD
|loc_0802957E|
|unk_0802957E|
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7DA
