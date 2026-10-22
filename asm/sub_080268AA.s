	CODE16
|sub_080268AA|
|unk_080268AA|
		ADD r0, sp, #8
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r1, r0, r1
		LDR r0, [sp, #0xc]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp]
		STR r1, [sp, #0x18]
		STR r0, [sp, #4]
		STR r0, [sp, #0x1c]
		ADD r0, sp, #0x20
		ADD r1, r4, #0
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x28]
		LDR r2, [sp, #0x2c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0x34]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp]
		SUB r0, r0, r1
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x34]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_0802690A|
		NEG r0, r2
|loc_0802690A|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_08026914|
		NEG r0, r0
|loc_08026914|
		STR r0, [sp, #0x34]
		ADD r0, r1, #0
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x34]
		CMP r0, #0x10
		BLT      |loc_08026924|
		CMP r1, #0x10
		BGE      |loc_08026928|
|loc_08026924|
		MOV r0, #1
		DCW     0xE7BE
|loc_08026928|
		MOV r0, #0
		DCW     0xE7BC
