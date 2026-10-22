	CODE16
|sub_08026DFE|
|unk_08026DFE|
		LDR r0, [pc, #0x178]
		LDR r5, [pc, #0x178]
		STR r0, [r4]
		MOV r0, #0x40
		STRH r0, [r4, #0xe]
		LDR r0, [r5]
		MOV r1, #0x40
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08026E24|
		MOV r1, #0x40
		LDR r0, [r5]
		BL       |sub_08011732|
		MOV r1, #0x40
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_08026E24|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x154]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [r7, #4]
		LDR r2, [r7]
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x1c]
		STR r6, [r4, #0x10]
		MOV r2, #0
		STR r2, [r4, #0x14]
		STR r2, [r4, #0x18]
		MOV r2, #0x37
		STRB r2, [r4, #8]
		STR r1, [r4, #4]
		LDR r1, [pc, #0x134]
		LDR r2, [pc, #0x13c]
		ADD r1, #4
		CMP r6, #0
		BEQ      |loc_08026E5A|
		LSL r0, r0, #5
		ADD r0, r0, r2
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		B        |loc_08026E66|
|loc_08026E5A|
		LSL r0, r0, #5
		ADD r0, r0, r2
		MOV r2, #0x40
		ADD r1, #0x80
		BL       |Thunk_VramCopy|
|loc_08026E66|
		ADD r0, r4, #0
		DCW     0xE7C8
