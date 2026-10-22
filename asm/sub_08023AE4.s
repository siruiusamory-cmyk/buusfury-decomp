	CODE16
|sub_08023AE4|
|unk_08023AE4|
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		LDR r2, [r1, #0xc]
		CMP r2, #0xa
		BHS      |loc_08023B50|
		ADR      r3, |loc_08023AF8|
		LDRB r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
|loc_08023AF8|
		LSL r4, r0, #0x10
		CMP r3, #0x18
		CMP r3, #0x18
		CMP r3, #0x18
		CMP r4, #0x2b
		LDR r3, [r1, #0x14]
		MOV r2, #0
		STR r2, [r3, #0x38]
		LDR r3, [r1, #0x18]
		STR r2, [r3, #0x38]
		LDR r2, [r1, #0xc]
		LSL r2, r2, #2
		ADD r0, r2, r0
		ADD r0, #0xff
		ADD r0, #1
		LDR r0, [r0, #0x14]
		STR r5, [r0, #0x38]
		LDR r0, [r1, #0xc]
		CMP r0, #0
		BEQ      |loc_08023B22|
		MOV r5, #0
|loc_08023B22|
		LDR r0, [pc, #0x160]
		LDR r0, [r0, #4]
		STRB r5, [r0]
		B        |loc_08023B50|
	INCBIN  baserom.gba_0x23b2a_0x23b50.extracted
