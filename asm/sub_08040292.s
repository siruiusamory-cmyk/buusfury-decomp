	CODE16
|sub_08040292|
|unk_08040292|
		LDR r4, [pc, #0xc4]
		MOV r5, #0
		LDR r4, [r4, #4]
		SUB r6, r4, r3
		LDRB r3, [r0]
		CMP r2, #0
		BEQ      |loc_080402D2|
|loc_080402A0|
		ADD r4, r5, #0
		ADD r5, #1
		CMP r4, #0x40
		BLT      |loc_080402AC|
		MOV r0, #0
		DCW     0xE7F0
|loc_080402AC|
		SUB r3, #1
		BPL      |loc_080402B2|
		MOV r3, #0x3f
|loc_080402B2|
		LSL r4, r3, #1
		ADD r4, r4, r0
		LDRH r4, [r4, #8]
		AND r4, r1
		BEQ      |loc_080402CE|
		LSL r4, r3, #2
		ADD r4, r4, r0
		ADD r4, #0x80
		LDR r4, [r4, #8]
		CMP r4, r6
		BGE      |loc_080402CC|
		MOV r0, #0
		DCW     0xE7E0
|loc_080402CC|
		SUB r2, #1
|loc_080402CE|
		CMP r2, #0
		BNE      |loc_080402A0|
|loc_080402D2|
		MOV r0, #1
		DCW     0xE7DB
