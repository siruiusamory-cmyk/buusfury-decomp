	CODE16
|sub_080040B2|
|unk_080040B2|
		MOV r3, #0
		STR r3, [r4]
		STR r3, [r4, #0x44]
		LDR r0, [r6]
		LDRB r1, [r0, #2]
		CMP r1, #0
		BEQ      |loc_080040E8|
		CMP r1, #4
		BNE      |loc_080040F4|
		LSL r0, r1, #9
		DCW     0xF039
		DCW     0xFA77
		ADD r5, r0, #0
		LDR r0, [r6]
		ADD r1, r0, #4
		ADD r0, r5, #0
		BL       |inc_0x049120_0x055620|
		ADD r2, r7, #0
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_08004038|
		ADD r0, r5, #0
		DCW     0xF039
		DCW     0xFAAB
		B        |loc_080040FE|
|loc_080040E8|
		ADD r2, r7, #0
		ADD r1, r0, #3
		ADD r0, r4, #0
		BL       |loc_08004038|
		B        |loc_080040FE|
|loc_080040F4|
		MOV r2, #0x3c
		ADR      r1, |inc_0x0158_0x143f2| + 0x4008
		LDR r0, [pc, #0x9c]
		BL       |Irq_WriteMaster1|
|loc_080040FE|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x3f58
