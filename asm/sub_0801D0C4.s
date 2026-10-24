	CODE16
|sub_0801D0C4|
|unk_0801D0C4|
		LDR r0, [pc, #0x32c]
		ADD r5, r4, #0
		STR r0, [r4]
		MOV r0, #0
		ADD r5, #0xff
		ADD r5, #1
		STR r0, [r4, #4]
		STR r0, [r5, #0xc]
		STR r0, [r5, #8]
		STR r0, [r5, #0x10]
		LDR r0, [pc, #0x31c]
		LDR r2, [pc, #0x320]
		STR r0, [r4]
		LDR r0, [r2, #0xc]
		LSL r1, r6, #2
		ADD r0, #0xe4
		ADD r0, r1, r0
		ADD r0, #4
		STR r0, [r5, #0x30]
		STR r6, [r5, #0x14]
		STR r7, [r5, #0x18]
		LDR r0, [r2, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r6, r0, r1
		MOV r0, #0x2c
		LDR r1, [pc, #0x2fc]
		MUL r0, r7
		ADD r7, r0, r1
		ADD r0, r6, #0
		BL       |Stats_GetLevel|
		LDRB r1, [r7, #0x15]
		CMP r0, r1
		BLT      |loc_0801D12A|
		LDRB r0, [r6, #0x14]
		LDR r1, [pc, #0x2ec]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDRB r0, [r0]
		LSL r0, r0, #0x1d
		LSR r0, r0, #0x1f
		BNE      |loc_0801D12A|
		MOV r0, #1
		B        |loc_0801D12C|
|loc_0801D12A|
		MOV r0, #0
|loc_0801D12C|
		STR r0, [r5, #0x20]
		LDR r2, [pc, #0x2cc]
		LDR r0, [r5, #0x30]
		LDR r2, [r2, #0xc]
		LDR r1, [r0]
		LDRB r2, [r2]
		LSR r1, r1, #0x1c
		SUB r1, #1
		CMP r1, r2
		BEQ      |loc_0801D144|
		MOV r1, #1
		B        |loc_0801D146|
|loc_0801D144|
		MOV r1, #0
|loc_0801D146|
		STR r1, [r5, #0x24]
		LDR r0, [r0]
		MOV r2, #1
		LSR r0, r0, #0x1c
		BNE      |loc_0801D152|
		MOV r2, #0
|loc_0801D152|
		ADD r0, r1, r2
		STR r0, [r5, #0x2c]
		STR r2, [r5, #0x28]
		ADD r0, r4, #0
		DCW     0xE7B2
