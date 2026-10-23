	CODE16
|sub_080079E2|
|unk_080079E2|
		LDRB r0, [r4, #6]
		ADD r0, #0xff
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r4, #6]
		BNE      |loc_08007A12|
		LDRB r0, [r4, #5]
		STRB r0, [r4, #6]
		BL       |loc_0803FAAC|
		MOV r6, #1
		LDRB r1, [r4, #4]
		LSL r6, r6, #0xf
		SUB r0, r0, r6
		MUL r0, r1
		ASR r0, r0, #0x13
		STR r0, [r4, #0xc]
		BL       |loc_0803FAAC|
		LDRB r1, [r4, #4]
		SUB r0, r0, r6
		MUL r0, r1
		ASR r0, r0, #0x13
		STR r0, [r4, #0x10]
|loc_08007A12|
		ADD r1, r4, #0
		ADD r1, #0xc
		LDR r0, [r5]
	INCBIN  baserom.gba_0x7a18_0x7a1a.extracted
|sub_08007A1A|
|unk_08007A1A|
	INCBIN	baserom.gba_0x7a1a_0x7a1e.extracted
|dat_08007A1E|
	DCW      0x0000
	DCW      0xa720
	DCW      0x0804
	DCW      0x07f4
	DCW      0x0807