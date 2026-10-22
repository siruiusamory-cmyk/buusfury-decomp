	CODE16
|sub_080402F0|
|unk_080402F0|
		LDRB r3, [r0]
|loc_080402F2|
		SUB r3, #1
		BPL      |loc_080402F8|
		MOV r3, #0x3f
|loc_080402F8|
		SUB r1, #1
		LSL r4, r1, #1
		LSL r5, r3, #1
		ADD r5, r5, r0
		LDRH r4, [r2, r4]
		LDRH r5, [r5, #8]
		CMP r4, r5
		BEQ      |loc_0804030C|
		MOV r0, #0
		DCW     0xE7EF
|loc_0804030C|
		CMP r1, #0
		BNE      |loc_080402F2|
		MOV r0, #1
		DCW     0xE7EB
