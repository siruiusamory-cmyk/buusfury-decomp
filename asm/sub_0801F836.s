	CODE16
|sub_0801F836|
|unk_0801F836|
		LDRB r2, [r3, #5]
		MOV r3, #0x2c
		MUL r2, r3
		LDR r3, [pc, #0x30c]
		ADD r2, r2, r3
		LDRH r2, [r2]
		LSL r2, r2, #2
		LDR r2, [r1, r2]
		MOV r1, #0x54
		BL       |loc_0803DCC4|
		B        |loc_0801F834|
|loc_0801F84E|
|unk_0801F84E|
		LDR r4, [r3]
		LDR r2, [pc, #0x2fc]
		CMP r4, #1
		BNE      |loc_0801F86A|
		LDRB r4, [r3, #5]
		MOV r3, #0x34
		MUL r3, r4
		ADD r2, r3, r2
		LDRH r2, [r2, #2]
		LSL r2, r2, #2
		LDR r1, [r1, r2]
		BL       |loc_0803DADA|
		B        |loc_0801F834|
|loc_0801F86A|
		LDRB r5, [r3, #5]
		MOV r3, #0x34
		MUL r3, r5
		ADD r2, r3, r2
		LDRH r2, [r2, #2]
		LSL r2, r2, #2
		LDR r2, [r1, r2]
		ADR      r1, |loc_0801FB3C|
		ADD r3, r4, #0
		BL       |sub_0803DC96|
		B        |loc_0801F834|
