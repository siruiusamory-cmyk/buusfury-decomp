	CODE16
|loc_08040950|
|unk_08040950|
; cited by 0x08040950 (a pc-relative load targets 0x08040990)
		LDR r0, [pc, #0x3c]
		LDR r0, [r0]
		LDRB r0, [r0, #8]
		LSL r0, r0, #1
		MOV r2, sp
		ADD r3, r0, r2
		ADD r3, #0x84
		MOV r0, #0
		STRH r0, [r3]
		SUB r3, #2
		MOV r4, #0
|loc_08040966|
		LDRH r2, [r5]
		ADD r5, #2
		MOV r0, #0
|loc_0804096C|
		STRH r2, [r3]
		SUB r3, #2
		LSR r2, r2, #1
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #0xf
		BLS      |loc_0804096C|
		ADD r0, r4, #1
		LSL r0, r0, #0x18
		LSR r4, r0, #0x18
		CMP r4, #3
		BLS      |loc_08040966|
		MOV r4, #0
		LDR r0, [pc, #4]
		ADD r2, r0, #0
		LDR r0, [r0]
		B        |loc_080409A2|
		DCD     g_EepromDescriptorPointer
|loc_08040994|
		STRH r1, [r3]
		SUB r3, #2
		LSR r1, r1, #1
		ADD r0, r4, #1
		LSL r0, r0, #0x18
		LSR r4, r0, #0x18
		LDR r0, [r2]
|loc_080409A2|
		LDRB r0, [r0, #8]
		CMP r4, r0
		BLO      |loc_08040994|
		MOV r0, #0
		STRH r0, [r3]
		SUB r3, #2
		MOV r6, #1
		STRH r6, [r3]
		MOV r4, #0xd0
		LSL r4, r4, #0x14
		LDR r0, [pc, #0x5c]
		LDR r0, [r0]
		LDRB r2, [r0, #8]
		ADD r2, #0x43
		MOV r0, sp
		ADD r1, r4, #0
		BL       |loc_080407E8|
		MOV r5, #0
		ADD r2, sp, #0xa4
		STRH r5, [r2]
		MOV r1, sp
		ADD r1, #0xa6
		LDR r0, [pc, #0x44]
		LDRH r0, [r0]
		STRH r0, [r1]
		ADD r0, sp, #0xac
		STR r5, [r0]
		LDRH r0, [r2]
		CMP r0, #0
		BNE      |loc_080409E8|
		LDRH r0, [r4]
		AND r0, r6
		CMP r0, #0
		DCW     0xD147
|loc_080409E8|
|unk_080409E8|
; cited by 0x080409B6 (a pc-relative load targets 0x08040A14)
		ADD r3, sp, #0xa8
		LDR r0, [pc, #0x2c]
		LDRH r0, [r0]
		STRH r0, [r3]
		MOV r4, sp
		ADD r4, #0xa6
		LDRH r1, [r3]
		LDRH r0, [r4]
		CMP r1, r0
		DCW     0xD032
		LDRH r1, [r3]
		LDRH r0, [r4]
		CMP r1, r0
		BLS      |loc_08040A1C|
		ADD r2, sp, #0xac
		LDRH r1, [r3]
		LDRH r0, [r4]
		SUB r1, r1, r0
		LDR r0, [r2]
		ADD r1, r1, r0
		STR r1, [r2]
		B        |loc_08040A32|
		DCD     g_EepromDescriptorPointer
		DCD     REG_VCOUNT
|loc_08040A1C|
		ADD r2, sp, #0xac
		ADD r0, sp, #0xa8
		LDRH r0, [r0]
		ADD r0, #0xe4
		MOV r1, sp
		ADD r1, #0xa6
		LDRH r1, [r1]
		SUB r0, r0, r1
		LDR r1, [r2]
		ADD r0, r0, r1
		STR r0, [r2]
|loc_08040A32|
		ADD r0, sp, #0xac
		LDR r0, [r0]
		CMP r0, #0x88
		DCW     0xD90E
		ADD r0, sp, #0xa4
		LDRH r0, [r0]
		CMP r0, #0
		DCW     0xD11F
		MOV r0, #0xd0
		LSL r0, r0, #0x14
		LDRH r0, [r0]
		MOV r1, #1
		AND r0, r1
		CMP r0, #0
		DCW     0xD118
		LDR r5, [pc, #0]
		DCW     0xE016
