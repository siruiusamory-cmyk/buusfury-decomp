|Irq_WriteEnableAndTimer3|
	CODE16
|unk_08040DDA|
		ADD r3, sp, #0
		LDRH r2, [r3, #4]
		LSL r2, r2, #0x1a
		LSR r2, r2, #0x1e
		BNE      |loc_08040E26|
		LDRH r2, [r3, #4]
		LSL r2, r2, #0x1c
		BPL      |loc_08040E42|
		LDRH r2, [r3, #4]
		LSL r2, r2, #0x18
		BMI      |loc_08040E42|
		LDRH r2, [r3, #4]
		LSL r2, r2, #0x1d
		BMI      |loc_08040E26|
		LDR r2, [r4, #0x14]
		CMP r2, #6
		BNE      |loc_08040E26|
		LDR r2, [pc, #0x98]
		MOV r3, #0
		STRH r3, [r2, #8]
		LDRH r3, [r2]
		MOV r6, #0x80
		BIC r3, r6
		MOV r6, #0x40
		ORR r3, r6
		STRH r3, [r2]
		STRH r5, [r2, #8]
		LDRH r3, [r1]
		LSR r6, r2, #0xc
		BIC r3, r6
		STRH r3, [r1]
		LDR r3, [pc, #0x84]
		LDR r1, [pc, #0xa0]
		STR r1, [r3, #0xc]
		MOV r1, #0xc0
		STRH r1, [r2, #2]
		MOV r1, #8
		STRB r1, [r4]
|loc_08040E26|
		STRB r5, [r4, #1]
|loc_08040E28|
|unk_08040E28|
		LDRB r1, [r4, #2]
		CMP r1, #0
		BEQ      |loc_08040E3E|
		LDRB r1, [r4, #8]
		CMP r1, #8
		BHS      |sub_08040E3A|
		ADD r1, #1
		STRB r1, [r4, #8]
		B        |loc_08040E3E|
