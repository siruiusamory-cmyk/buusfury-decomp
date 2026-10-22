	CODE16
|sub_08021CD0|
|unk_08021CD0|
; cited by 0x08021BD4 (a pc-relative load targets 0x08021D48)
		LDR r0, [r4, #0x18]
		LDR r6, [pc, #0x1e0]
		CMP r0, #0
		BEQ      |loc_08021CDE|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BLE      |loc_08021DAC|
|loc_08021CDE|
		LDR r0, [r6, #0xc]
		BL       |sub_08011A1E|
		LDR r0, [r4, #8]
		MOV r2, #0x80
		LDR r1, [r0]
		MOV r5, #0
		LDR r2, [r2, r1]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BNE      |loc_08021D00|
		MOV r5, #1
|loc_08021D00|
		LDR r0, [r4, #0xc]
		MOV r2, #0x80
		LDR r1, [r0]
		LDR r2, [r2, r1]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BNE      |loc_08021D1C|
		MOV r0, #2
		ORR r5, r0
|loc_08021D1C|
		LDR r1, [r7, #4]
		CMP r1, #0
		BEQ      |loc_08021D3A|
		LDR r0, [r4, #0x30]
		SUB r0, #1
		STR r0, [r4, #0x30]
		BNE      |loc_08021D3A|
		MOV r0, #0x3c
		STR r0, [r4, #0x30]
		SUB r1, #1
		STR r1, [r7, #4]
		ORR r1, r5
		BNE      |loc_08021D3A|
		MOV r0, #1
		STR r0, [r7, #0x10]
|loc_08021D3A|
		MOV r1, #0xff
		LDR r0, [r4, #0x2c]
		ADD r1, #0x1d
		CMP r0, r1
		BLT      |loc_08021D48|
		MOV r0, #1
		STR r0, [r7, #0x10]
|loc_08021D48|
		LDR r0, [r7, #4]
		ORR r0, r5
		BNE      |loc_08021D52|
		MOV r5, #3
		B        |loc_08021D56|
|loc_08021D52|
		CMP r5, #0
		BEQ      |loc_08021DEA|
|loc_08021D56|
		LDR r0, [r4, #0x24]
		CMP r0, #0
		BNE      |loc_08021DC2|
		LDR r1, [pc, #0x154]
		ADD r1, #0x34
		CMP r5, #1
		BNE      |loc_08021D86|
		LDR r0, [r6, #0x20]
		LDR r0, [r0, #4]
		LDRB r2, [r7, #1]
		ASR r0, r0, #1
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_08021D7C|
		MOV r0, #0x73
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021D7C|
		MOV r0, #0x70
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021D86|
		CMP r5, #2
		BNE      |loc_08021DAE|
		LDR r0, [r6, #0x20]
		LDR r0, [r0, #4]
		LDRB r2, [r7]
		ASR r0, r0, #1
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_08021DA2|
		MOV r0, #0x72
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021DA2|
		MOV r0, #0x6f
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
		B        |loc_08021DB6|
|loc_08021DAC|
		B        |loc_08021E0A|
|loc_08021DAE|
		MOV r0, #0x71
		BL       |sub_0802BFBC|
		STR r0, [r4, #0x24]
|loc_08021DB6|
		LDR r1, [r4, #0x24]
		LDR r0, [r6, #0xc]
		BL       |List_Append|
		MOV r0, #0x3c
		STR r0, [r4, #0x28]
|loc_08021DC2|
		LDR r0, [r4, #0x2c]
		MOV r1, #0xff
		ADD r0, #1
		ADD r1, #0x2d
		CMP r0, r1
		STR r0, [r4, #0x2c]
		BLT      |loc_08021DEE|
		LDR r1, [r4, #0x1c]
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
		LDR r0, [r4, #0x24]
		CMP r0, #0
		BEQ      |loc_08021DE6|
		ADD r1, r0, #0
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
|loc_08021DE6|
		ADD r0, r5, #0
		DCW     0xE771
|loc_08021DEA|
		MOV r0, #0
		STR r0, [r4, #0x2c]
|loc_08021DEE|
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BEQ      |loc_08021DFA|
		SUB r0, #1
		STR r0, [r4, #0x28]
		B        |loc_08021E0A|
|loc_08021DFA|
		LDR r1, [r7, #0x14]
		LDR r0, [r6, #0x1c]
		BL       |loc_080126D4|
		LDR r1, [r7, #0x18]
		LDR r0, [r6, #0x1c]
		BL       |loc_080126D4|
|loc_08021E0A|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		DCW     0xD143
		LDR r0, [r6, #0x14]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1c
		LSR r1, r0, #0x1f
		BNE      |loc_08021E24|
		LDR r0, [r6, #0x10]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1f
		BEQ      |loc_08021EAA|
|loc_08021E24|
		LDR r0, [r4, #0x18]
		CMP r0, #0
		BNE      |loc_08021E50|
		MOV r1, #0
		STR r1, [r4, #0x20]
		LDR r1, [r6, #0x14]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		BEQ      |loc_08021E3C|
		MOV r1, #1
		STR r1, [r4, #0x20]
|loc_08021E3C|
		LDR r1, [r6, #0x10]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		BEQ      |loc_08021E6A|
		LDR r1, [r4, #0x20]
		MOV r2, #2
		ORR r1, r2
		STR r1, [r4, #0x20]
		B        |loc_08021E6A|
|loc_08021E50|
		CMP r1, #0
		BEQ      |loc_08021E5A|
		LDR r1, [r4, #0x20]
		LSL r1, r1, #0x1f
		BMI      |loc_08021E6A|
|loc_08021E5A|
		LDR r1, [r6, #0x10]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1c
		LSR r1, r1, #0x1f
		BEQ      |loc_08021EAA|
		LDR r1, [r4, #0x20]
		LSL r1, r1, #0x1e
		BPL      |loc_08021EAA|
|loc_08021E6A|
		MOV r1, #1
		CMP r0, #0
		BEQ      |loc_08021E72|
		MOV r1, #0
|loc_08021E72|
		STR r1, [r4, #0x18]
		CMP r1, #0
		DCW     0xD00A
		LDR r1, [pc, #0x38]
		ADD r1, #0x3c
		MOV r0, #0x27
		BL       |sub_0802BFBC|
		ADD r1, r0, #0
		STR r0, [r4, #0x14]
		LDR r0, [r6, #0xc]
		BL       |List_Append|
|loc_08021E8C|
|unk_08021E8C|
		B        |loc_08021EAA|
		LDR r1, [r4, #0x14]
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
		B        |loc_08021EAA|
		LDR r0, [r4, #0x18]
		CMP r0, #0
		BEQ      |loc_08021EAA|
		MOV r0, #0
		STR r0, [r4, #0x18]
		LDR r1, [r4, #0x14]
		LDR r0, [r6, #0xc]
		BL       |loc_08011944|
