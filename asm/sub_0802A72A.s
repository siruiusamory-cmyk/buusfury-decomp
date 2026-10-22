	CODE16
|sub_0802A72A|
|unk_0802A72A|
		LDR r2, [r1, #0x30]
		CMP r2, r0
		BNE      |loc_0802A734|
		MOV r0, #0
		DCW     0xE7F8
|loc_0802A734|
		LDRB r2, [r1, #0x14]
		LDR r3, [r0, #0x44]
		MOV r7, #1
		EOR r3, r7
		CMP r2, r3
		BEQ      |loc_0802A744|
		MOV r0, #0
		DCW     0xE7F0
|loc_0802A744|
		LDR r2, [r0, #0x40]
		LDR r3, [r0, #0x38]
		LDR r4, [r0, #0x3c]
		MUL r3, r2
		MUL r4, r2
		ADD r2, r3, #0
		STR r3, [sp, #4]
		ADD r3, r4, #0
		STR r4, [sp, #8]
		LDR r4, [r0, #0x20]
		ADD r1, #4
		ADD r2, r4, r2
		LDR r4, [r0, #0x24]
		STR r2, [sp, #4]
		ADD r3, r4, r3
		STR r3, [sp, #8]
		ADD r5, r3, #0
		ADD r4, r2, #0
		LDR r6, [r1]
		ADD r4, #0xc
		SUB r2, #0xc
		ADD r5, #0xc
		SUB r3, #0xc
		CMP r6, r4
		BGE      |loc_0802A78E|
		LDR r4, [r1, #8]
		CMP r2, r4
		BGE      |loc_0802A78E|
		LDR r2, [r1, #4]
		CMP r2, r5
		BGE      |loc_0802A78E|
		LDR r1, [r1, #0xc]
		CMP r3, r1
		BGE      |loc_0802A78E|
		STRB r7, [r0, #0x10]
		MOV r0, #1
		DCW     0xE7CB
|loc_0802A78E|
		MOV r0, #0
		DCW     0xE7C9
|loc_0802A792|
|unk_0802A792|
		MOV r1, #0
		MVN r1, r1
		STR r1, [r0, #0x18]
		MOV r0, #0
		DCW     0xE7C4
|loc_0802A79C|
|unk_0802A79C|
		MOV r0, #0
		DCW     0xE7C2
