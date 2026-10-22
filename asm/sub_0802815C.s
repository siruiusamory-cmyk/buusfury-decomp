	CODE16
|sub_0802815C|
|unk_0802815C|
		LDR r0, [pc, #0x20c]
		MOV r5, #5
		LSL r5, r5, #0xb
		LDR r6, [pc, #0x20c]
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r6, #4]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08028184|
		ADD r1, r5, #0
		LDR r0, [r6, #4]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
|loc_08028184|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x1ec]
		MOV r2, #0x40
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0x34
		MOV r1, #0xa0
		ADD r5, r0, #0
		BL       |loc_0803F540|
		MOV r2, #0x40
		MOV r1, #0xa0
		ADD r0, r4, #0
		ADD r0, #0x68
		BL       |loc_0803F540|
		MOV r1, #8
		SUB r1, r1, r7
		MOV r0, #0
		STR r0, [r4, #0x10]
		STRB r0, [r4, #8]
		LSL r3, r1, #1
		ADD r1, r3, r1
		STR r0, [r4, #4]
		STR r1, [r4, #0x20]
		STR r0, [r4, #0x14]
		LDR r0, [pc, #0x1bc]
		ADD r7, r4, #0
		STR r0, [r4, #0x30]
		ADD r7, #0x80
		LDR r1, [r7, #0xc]
		LDR r0, [pc, #0x1b8]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r2, [pc, #0x1b0]
		LDR r0, [r4, #0x58]
		LDR r1, [r7, #0xc]
		LDR r2, [r2, #4]
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		BL       |loc_08027E48|
		MOV r7, #0
|loc_080281DC|
		MOV r0, #6
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r1, r4, r7
		ADD r1, #0x20
		ADD r7, #1
		CMP r7, #5
		STRB r0, [r1, #4]
		BLT      |loc_080281DC|
		MOV r0, #2
		STRB r0, [r5, #3]
		LDR r0, [pc, #0x18c]
		MOV r1, #1
		STRB r1, [r5, #2]
		STR r0, [r5, #0x20]
		STRB r1, [r5]
		LDR r0, [r6, #8]
		LDR r1, [pc, #0x184]
		STR r0, [r4, #0x40]
		MOV r0, #0x50
		STR r0, [r4, #0x38]
		MOV r0, #0x1c
		STR r0, [r4, #0x3c]
		MOV r0, #0x25
		LSL r0, r0, #4
		LDR r1, [r1, r0]
		ADD r0, r5, #0
		BL       |loc_0803DADA|
		ADD r0, r4, #0
		DCW     0xE79F
