	CODE16
|sub_08021B4A|
|unk_08021B4A|
		LDR r1, [pc, #0x68]
		LDRB r0, [r1, #1]
		ADD r0, #1
		STRB r0, [r1, #1]
		B        |loc_08021B5C|
|loc_08021B54|
|unk_08021B54|
		LDR r1, [pc, #0x5c]
		LDRB r0, [r1]
		ADD r0, #1
		STRB r0, [r1]
|loc_08021B5C|
|unk_08021B5C|
		MOV r0, #0xc
		DCW     0xF01B
		DCW     0xFD2B
		CMP r0, #0
		BEQ      |loc_08021B74|
		LDR r1, [pc, #0x8c]
		STR r1, [r0]
		MOV r1, #0xff
		ADD r1, #1
		STR r1, [r0, #4]
		MOV r1, #4
		STR r1, [r0, #8]
|loc_08021B74|
		BL       |inc_0x03d784_0x041118| + 0x11c
		LDR r0, [pc, #0x38]
		LDR r0, [r0, #0x14]
		BL       |inc_0x0158_0x143f2| + 0x1059e
		LDR r0, [pc, #0x30]
		LDR r0, [r0, #0x18]
		BL       |inc_0x0158_0x143f2| + 0x1059e
		LDR r0, [pc, #0x2c]
		LDR r0, [r0, #0xc]
		BL       |loc_08011B04|
		ADD r3, r7, #1
		BNE      |loc_08021B98|
		MOV r0, #1
		DCW     0xE7D6
|loc_08021B98|
		LDR r7, [pc, #0x1c]
		LDR r1, [pc, #0x18]
		LDR r0, [r7, #0x20]
		LDR r0, [r0, #4]
		LDRB r2, [r1]
		ASR r0, r0, #1
		CMP r0, r2
		BLT      |loc_08021BB0|
		LDRB r1, [r1, #1]
		CMP r0, r1
		BLT      |loc_08021BB0|
		B        |loc_08021950|
|loc_08021BB0|
		MOV r0, #1
		DCW     0xE7C8
	INCBIN  baserom.gba_0x21bb4_0x21bb6.extracted
