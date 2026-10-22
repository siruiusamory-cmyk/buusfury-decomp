	CODE16
|sub_08029EF6|
|unk_08029EF6|
		ADD r0, sp, #0x2c
		BL       |loc_0800FE78|
		ADD r1, r4, #0
		ADD r0, sp, #0x1c
		BL       |loc_0800FE78|
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x28]
		ADD r0, r0, r1
		LDR r1, [sp, #0x20]
		STR r0, [sp, #0xc]
		ADD r1, r1, r2
		STR r1, [sp, #0x10]
		ASR r1, r1, #1
		ASR r0, r0, #1
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		MOV ip, r1
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		LDR r1, [sp, #0x24]
		LDR r0, [sp, #0x1c]
		LDR r5, [sp, #0x28]
		LDR r2, [sp, #0x34]
		ADD r1, #3
		SUB r0, #4
		SUB r5, #6
		CMP r0, r2
		LDR r6, [sp, #0x20]
		BGE      |loc_08029F48|
		LDR r2, [sp, #0x2c]
		CMP r2, r1
		BGE      |loc_08029F48|
		LDR r2, [sp, #0x38]
		CMP r6, r2
		BGE      |loc_08029F48|
		LDR r2, [sp, #0x30]
		CMP r2, r5
		BLT      |loc_08029F4C|
|loc_08029F48|
		MOV r0, #0
		DCW     0xE7D2
|loc_08029F4C|
		LDR r2, [sp, #0x2c]
		LDR r3, [sp, #0x34]
		LDR r7, [sp, #0x38]
		ADD r3, r2, r3
		LDR r2, [sp, #0x30]
		STR r3, [sp]
		ADD r2, r2, r7
		STR r2, [sp, #4]
		ASR r2, r2, #1
		ASR r3, r3, #1
		STR r2, [sp, #4]
		STR r2, [sp, #0xc]
		ADD r2, r3, #0
		STR r3, [sp]
		STR r3, [sp, #8]
		LDR r3, [sp, #0x14]
		LDR r7, [sp, #0x18]
		SUB r2, r2, r3
		LDR r3, [sp, #0xc]
		STR r2, [sp]
		SUB r7, r3, r7
		ADD r3, r2, #0
		CMP r2, #0
		STR r7, [sp, #4]
		STR r7, [sp, #0x10]
		BGE      |loc_08029F82|
		NEG r3, r2
|loc_08029F82|
		LDR r7, [sp, #0x10]
		CMP r7, #0
		BGE      |loc_08029F8A|
		NEG r7, r7
|loc_08029F8A|
		CMP r3, r7
		BLE      |loc_08029FA8|
		LDR r5, [sp, #0x28]
		MOV r6, ip
		ADD r5, #3
		CMP r2, #0
		BLE      |loc_08029FA0|
		MOV r0, #3
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x14]
		B        |loc_08029FC6|
|loc_08029FA0|
		MOV r1, #2
		STRB r1, [r4, #0x10]
		LDR r1, [sp, #0x14]
		B        |loc_08029FC6|
|loc_08029FA8|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |sub_0800FDFA|
		LDR r7, [sp, #0x10]
		LDR r0, [sp]
		LDR r1, [sp, #8]
		CMP r7, #0
		BLE      |loc_08029FC0|
		MOV r2, #0
		STRB r2, [r4, #0x10]
		B        |loc_08029FC6|
|loc_08029FC0|
		MOV r2, #1
		STRB r2, [r4, #0x10]
		LDR r5, [sp, #4]
|loc_08029FC6|
		LDR r2, [sp, #0x34]
		CMP r0, r2
		BGE      |loc_08029FE2|
		LDR r0, [sp, #0x2c]
		CMP r0, r1
		BGE      |loc_08029FE2|
		LDR r0, [sp, #0x38]
		CMP r6, r0
		BGE      |loc_08029FE2|
		LDR r0, [sp, #0x30]
		CMP r0, r5
		BGE      |loc_08029FE2|
		MOV r0, #1
		DCW     0xE787
|loc_08029FE2|
		MOV r0, #0
		DCW     0xE785
