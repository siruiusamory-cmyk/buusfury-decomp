	CODE16
|sub_08010D58|
|unk_08010D58|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10bfe
|loc_08010D5C|
|unk_08010D5C|
		LDR r1, [pc, #0x1d4]
		LSL r0, r5, #2
		LDR r0, [r1, r0]
		LDR r1, [r4, #0x14]
		CMP r1, r0
		BNE      |loc_08010D78|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800EEB0|
		CMP r0, #0
		BEQ      |loc_08010D78|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10bfe
|loc_08010D78|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10bfe
