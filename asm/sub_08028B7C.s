	CODE16
|sub_08028B7C|
|unk_08028B7C|
		LDR r1, [r2, #0x30]
		ADD r5, r2, #0
		CMP r1, r0
		BNE      |loc_08028B88|
		MOV r0, #0
		DCW     0xE7F7
|loc_08028B88|
		LDRB r1, [r5, #0x14]
		LDR r2, [r0, #0x44]
		MOV r3, #1
		EOR r2, r3
		CMP r1, r2
		BEQ      |loc_08028B98|
		MOV r0, #0
		DCW     0xE7EF
|loc_08028B98|
		LDR r1, [r0, #0x40]
		LDR r2, [r0, #0x38]
		LDR r3, [r0, #0x3c]
		MUL r2, r1
		MUL r3, r1
		ADD r1, r2, #0
		STR r2, [sp, #4]
		ADD r2, r3, #0
		STR r3, [sp, #8]
		LDR r3, [r0, #0x20]
		LDR r0, [r0, #0x24]
		ADD r1, r3, r1
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ADD r2, r0, #0
		ADD r4, r0, #0
		ADD r0, r5, #4
		STR r1, [sp, #4]
		ADD r3, r1, #0
		LDR r5, [r5, #4]
		ADD r3, #0xc
		SUB r1, #0xc
		ADD r4, #0xc
		SUB r2, #0xc
		CMP r5, r3
		BGE      |loc_08028BE2|
		LDR r3, [r0, #8]
		CMP r1, r3
		BGE      |loc_08028BE2|
		LDR r1, [r0, #4]
		CMP r1, r4
		BGE      |loc_08028BE2|
		LDR r0, [r0, #0xc]
		CMP r2, r0
		BGE      |loc_08028BE2|
		MOV r0, #1
		DCW     0xE7CA
|loc_08028BE2|
		MOV r0, #0
		DCW     0xE7C8
|loc_08028BE6|
|unk_08028BE6|
		MOV r0, #0
		DCW     0xE7C6
|loc_08028BEA|
|unk_08028BEA|
		MOV r0, #0
		DCW     0xE7C4
