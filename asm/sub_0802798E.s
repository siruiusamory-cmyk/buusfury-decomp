	CODE16
|sub_0802798E|
|unk_0802798E|
		CMP r0, #0
		BGE      |loc_08027996|
		ADD r0, r4, #0
		DCW     0xE7FA
|loc_08027996|
|unk_08027996|
		ADD r4, #1
		CMP r4, #0xe8
		DCW     0xDBE2
		LDR r6, [pc, #0x3c]
		MOV r4, #0
|loc_080279A0|
		LDR r1, [pc, #0x34]
		LSL r0, r4, #4
		ADD r0, r0, r1
		CMP r5, #0
		BEQ      |loc_080279BC|
		LDR r1, [r0, #0xc]
		CMP r1, #0
		BLT      |loc_080279CA|
		LSL r3, r1, #3
		SUB r1, r3, r1
		LSL r1, r1, #2
		ADD r1, r1, r6
		CMP r1, r5
		BNE      |loc_080279CA|
|loc_080279BC|
		LDR r0, [r0, #4]
		BL       |inc_0x0158_0x143f2|
		CMP r0, r7
		BNE      |loc_080279CA|
		ADD r0, r4, #0
		DCW     0xE7E0
|loc_080279CA|
		ADD r4, #1
		CMP r4, #0xe8
		BLT      |loc_080279A0|
		MOV r0, #0
		MVN r0, r0
		DCW     0xE7DA
|sub_080279D6|
	DCW      0x0000
	DCW      0xd380
	DCW      0x0874
	DCW      0x1274
	DCW      0x0871
