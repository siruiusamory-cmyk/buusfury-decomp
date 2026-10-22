	CODE16
|sub_080085D8|
|unk_080085D8|
		LDRB r5, [r3, #4]
		CMP r0, r5
		BLT      |loc_080085E0|
		SUB r0, r0, r5
|loc_080085E0|
|unk_080085E0|
		LDR r3, [r4, #4]
		ADD r5, r2, #0
		LDRB r3, [r3, #4]
		ADD r1, #1
		MUL r5, r3
		ADD r0, r5, r0
		STMIA r7!, {r0}
		CMP r1, #1
		BLE      |inc_0x0158_0x143f2| + 0x846e
		ADD r6, #1
		CMP r6, #1
		BLE      |inc_0x0158_0x143f2| + 0x8452
		MOV r6, #0
		MOV r5, #0
		MOV r1, #0
|loc_080085FE|
		LSL r0, r1, #2
		ADD r2, sp, #0x3fc
		ADD r2, #8
		LDR r2, [r2, r0]
		MOV ip, r0
		LDR r0, [r4, #4]
		LSL r3, r2, #2
		ADD r0, r0, r3
		LDR r0, [r0, #8]
		CMP r0, #0
		BNE      |loc_08008624|
		LDR r0, [pc, #0x220]
		MOV r2, ip
		ADD r2, r2, r4
		STR r0, [r2, #8]
		MOV r0, #1
		LSL r0, r1
		ORR r6, r0
		B        |loc_08008656|
|loc_08008624|
		MOV r0, #0
|loc_08008626|
		LSL r7, r0, #2
		ADD r3, r7, r4
		LDR r7, [r3, #0x2c]
		CMP r7, r2
		BNE      |loc_08008650|
		MOV r7, #1
		ADD r2, r7, #0
		LSL r2, r0
		ORR r5, r2
		LSL r7, r1
		ADD r2, r7, #0
		ORR r6, r2
		MOV r2, #0x1d
		LSL r0, r0, #0xa
		ADD r0, r0, r4
		LSL r2, r2, #5
		ADD r0, r0, r2
		MOV r2, ip
		ADD r2, r2, r4
		STR r0, [r2, #8]
		B        |loc_08008656|
|loc_08008650|
		ADD r0, #1
		CMP r0, #9
		BLT      |loc_08008626|
|loc_08008656|
		ADD r1, #1
		CMP r1, #9
		BLT      |loc_080085FE|
		MOV r7, #0
|loc_0800865E|
|unk_0800865E|
		MOV r2, #1
		ADD r0, r2, #0
		LSL r0, r7
		AND r0, r6
		BNE      |inc_0x0158_0x143f2| + 0x8566
		MOV r1, #0
|loc_0800866A|
|unk_0800866A|
		ADD r0, r2, #0
		LSL r0, r1
		AND r0, r5
		BNE      |inc_0x0158_0x143f2| + 0x8560
		LSL r2, r1
		ORR r5, r2
		LSL r2, r1, #2
		LSL r0, r7, #2
		ADD r3, sp, #0x3fc
		ADD r3, #8
		MOV ip, r0
		LDR r0, [r3, r0]
		ADD r2, r2, r4
		STR r0, [r2, #0x2c]
		MOV r2, #0x1d
		LSL r1, r1, #0xa
		ADD r1, r1, r4
		LSL r2, r2, #5
		ADD r1, r1, r2
		MOV r2, ip
		ADD r3, sp, #0x3fc
		STR r1, [r3, #0x2c]
		ADD r2, r2, r4
		STR r1, [r2, #8]
		LDR r1, [r4, #4]
		LSL r0, r0, #2
		ADD r0, r1, r0
		LDR r0, [r0, #8]
		ADD r1, sp, #4
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r2, #1
		ADD r3, sp, #0x3fc
		LDR r0, [r3, #0x2c]
		LSL r2, r2, #0xa
		ADD r1, sp, #4
	INCBIN  baserom.gba_0x86b2_0x86b4.extracted
|sub_080086B4|
|unk_080086B4|
	INCBIN	baserom.gba_0x86b4_0x86b8.extracted
	ADD      r1, #1
	CMP      r1, #9
	BLT      |loc_0800866A|
	ADD      r7, #1
	CMP      r7, #9
	BLT      |loc_0800865E|
	ADD      r3, sp, #0x3fc
	LDR      r1, [r3, #0x34]
	LDR      r2, [r1]
	LDR      r1, [r1, #4]
	STR      r1, [r4, #0x54]
	STR      r2, [r4, #0x50]
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
