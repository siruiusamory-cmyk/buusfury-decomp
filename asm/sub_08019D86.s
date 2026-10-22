	CODE16
|sub_08019D86|
|unk_08019D86|
		LDR r1, [pc, #0x238]
		LDR r1, [r1, #0x14]
		LDR r1, [r1, #0xc]
		CMP r1, #0
		BNE      |loc_08019D94|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x4992
|loc_08019D94|
		LDRB r1, [r0, #0x15]
		LSL r1, r1, #1
		ADD r1, r1, r0
		ADD r1, #0x2e
		LDRB r1, [r1]
		LDR r2, [pc, #0x220]
		LDRB r1, [r2, r1]
		BL       |inc_0x0158_0x143f2| + 0x13360
		B        |inc_0x153f2_0x1a3f2| + 0x4992
