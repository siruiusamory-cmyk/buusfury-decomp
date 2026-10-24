	CODE16
|sub_08029B6C|
|unk_08029B6C|
		LDR r2, [pc, #0x68]
		LDR r0, [r1, #0x14]
		CMP r0, r2
		BEQ      |loc_08029B78|
		MOV r0, #0
		DCW     0xE7F7
|loc_08029B78|
		ADD r0, sp, #0x10
		BL       |Object_GetPoints|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |Object_GetPoints|
		LDR r0, [sp]
		LDR r1, [sp, #4]
		LDR r2, [sp, #8]
		LDR r3, [sp, #0xc]
		LDR r4, [sp, #0x18]
		SUB r0, #8
		SUB r1, #8
		ADD r2, #8
		ADD r3, #8
		CMP r0, r4
		BGE      |loc_08029BB2|
		LDR r0, [sp, #0x10]
		CMP r0, r2
		BGE      |loc_08029BB2|
		LDR r0, [sp, #0x1c]
		CMP r1, r0
		BGE      |loc_08029BB2|
		LDR r0, [sp, #0x14]
		CMP r0, r3
		BGE      |loc_08029BB2|
		MOV r0, #1
		DCW     0xE7DA
|loc_08029BB2|
		MOV r0, #0
		DCW     0xE7D8
