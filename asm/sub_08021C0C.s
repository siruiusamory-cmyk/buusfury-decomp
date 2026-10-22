	CODE16
|sub_08021C0C|
|unk_08021C0C|
		LDR r0, [pc, #0x2a0]
		LDR r5, [pc, #0x2a4]
		STR r0, [r4]
		LDR r0, [r5, #0x10]
		MOV r1, #1
		ADD r0, #0xff
		ADD r0, #0x81
		STRH r1, [r0, #0x10]
		STR r1, [r0, #0x14]
		MOV r1, #0
		STR r1, [r0, #0x18]
		LDR r0, [r5, #0x14]
		ADD r0, #0xff
		ADD r0, #0x91
		MOV r2, #4
		BL       |sub_08049168|
		LDR r0, [r5, #0x10]
		MOV r2, #4
		ADD r0, #0xff
		ADD r0, #0x9d
		MOV r1, #0
		BL       |sub_08049168|
		ADD r0, r4, #0
		DCW     0xE7E4
