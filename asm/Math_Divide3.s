|Math_Divide3|
	CODE16
|unk_0800EFD0|
		MOV r2, #1
		STR r2, [sp, #0x24]
		LDR r2, [r5, #4]
		MOV r7, sp
		ADD r6, r2, #0
		ADD r2, #0x20
		STR r2, [r5, #4]
		ADD r2, r1, #1
		STR r2, [r5, #8]
		MOV r2, #8
		ADD r7, r7, r2
		STR r1, [sp, #0x20]
		ADD r1, r7, #0
		ADD r3, r0, #0
		MOV r0, sp
		ADD r1, #0x18
		ADD r0, r0, r2
		BL       |__vecmap1c__FPvT1iPFPv_v|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r1, [r3, #0x3c]
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x2570
		LDR r0, [r4, #0x68]
		STRH r0, [r6, #6]
		MOV r0, #0
		STRH r0, [r6, #0xe]
		STRH r0, [r6, #0x16]
		LDR r0, [r4, #0x68]
		STRH r0, [r6, #0x1e]
		LDR r0, [r4, #0x54]
		LDR r0, [r0, #0xc]
		LSL r0, r0, #3
		BPL      |loc_0800F08E|
		LDRH r1, [r6, #6]
		ADD r3, sp, #0
		NEG r1, r1
		STRH r1, [r3]
		LDR r1, [sp]
		STR r1, [sp, #4]
		LDRH r1, [r3, #4]
		STRH r1, [r6, #6]
		B        |loc_0800F08E|
|loc_0800F02C|
|unk_0800F02C|
; cited by 0x0800EE02 (a pc-relative load targets 0x0800F1E4)
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r1, [r3, #0x3c]
		LDR r1, [r1]
		CMP r1, #0
		BEQ      |loc_0800F08E|
		LDR r1, [r5, #8]
		CMP r1, #0x10
		BLT      |loc_0800F044|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xee72
|loc_0800F044|
		MOV r2, #1
		STR r2, [sp, #0x24]
		LDR r2, [r5, #4]
		ADD r3, r0, #0
		ADD r6, r2, #0
		ADD r2, #0x20
		STR r2, [r5, #4]
		ADD r2, r1, #1
		STR r2, [r5, #8]
		STR r1, [sp, #0x20]
		MOV r1, sp
		MOV r2, #8
		ADD r1, r1, r2
		ADD r1, #0x18
		MOV r0, sp
		ADD r0, r0, r2
		BL       |__vecmap1c__FPvT1iPFPv_v|
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r1, [r3, #0x3c]
		ADD r0, sp, #8
		BL       |inc_0x03d784_0x041118| + 0x2570
		LDR r0, [sp, #8]
		ASR r0, r0, #2
		STRH r0, [r6, #6]
		LDR r0, [sp, #0x10]
		ASR r0, r0, #2
		STRH r0, [r6, #0xe]
		LDR r0, [sp, #0xc]
		ASR r0, r0, #2
		STRH r0, [r6, #0x16]
		LDR r0, [sp, #0x14]
		ASR r0, r0, #2
		STRH r0, [r6, #0x1e]
|loc_0800F08E|
		LDR r0, [r4, #0x60]
		CMP r0, #0
		BEQ      |loc_0800F17A|
		LDR r0, [r4, #0x4c]
		CMP r0, #0
		BEQ      |loc_0800F130|
		LDR r0, [r5]
		ADD r6, r0, #0
		ADD r0, #8
		STR r0, [r5]
		LDRB r1, [r4, #0x11]
		LDR r0, [r4, #0x4c]
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r1, [r4, #0x10]
		LSL r1, r1, #1
		ADD r7, r0, r1
		LDRB r0, [r7]
		CMP r0, #0x80
		BEQ      |loc_0800F130|
		LDR r3, [sp, #0x24]
		CMP r3, #0
		BEQ      |loc_0800F132|
		LDR r1, [sp, #0x20]
		MOV r0, #0x63
		LSL r1, r1, #0x1b
		LSR r1, r1, #2
		LSL r0, r0, #8
		ORR r0, r1
		STR r0, [r6]
		MOV r3, #0
		LDRSB r0, [r7, r3]
		LDR r1, [r4, #0x68]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #6
		SWI 6
		LDR r1, [r4, #0x6c]
		MOV r3, #1
		ADD r0, r0, r1
		SUB r0, #8
		LDR r1, [r6]
		LDR r2, [pc, #0x114]
		LSL r0, r0, #0x17
		LSR r0, r0, #7
		AND r1, r2
		ORR r0, r1
		STR r0, [r6]
		LDRSB r0, [r7, r3]
		LDR r1, [r4, #0x68]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #6
		SWI 6
		LDR r1, [r4, #0x70]
		MOV r2, #3
		ADD r0, r0, r1
		LDR r1, [r6]
		ADD r0, #0xf4
		LSL r0, r0, #0x18
		LSR r1, r1, #8
		LSL r1, r1, #8
		LSR r0, r0, #0x18
		ORR r0, r1
		STR r0, [r6]
		LDRB r0, [r4, #8]
		LDR r1, [r6, #4]
		LSL r2, r2, #0xa
		LSL r0, r0, #0x1a
		LSR r0, r0, #0x1e
		LSL r0, r0, #0xa
		BIC r1, r2
		ORR r0, r1
		LDR r1, [pc, #0xc0]
		LSR r0, r0, #0xa
		LDRH r1, [r1, #2]
		LSL r0, r0, #0xa
		LSL r1, r1, #0x16
		LSR r1, r1, #0x16
		ORR r0, r1
		STR r0, [r6, #4]
|loc_0800F130|
		B        |loc_0800F180|
|loc_0800F132|
		MOV r0, #3
		LSL r0, r0, #0xd
		STR r0, [r6]
		MOV r3, #0
		LDRSB r2, [r7, r3]
		LDR r1, [r4, #0x6c]
		ADD r1, r1, r2
		LSL r1, r1, #0x17
		LSR r1, r1, #7
		ORR r0, r1
		STR r0, [r6]
		LDRB r2, [r7, #1]
		LDR r1, [r4, #0x70]
		LSR r0, r0, #8
		ADD r1, r1, r2
		LSL r1, r1, #0x18
		LSR r1, r1, #0x18
		LSL r0, r0, #8
		ORR r0, r1
		STR r0, [r6]
		LDRB r0, [r4, #8]
		LDR r1, [r6, #4]
		MOV r2, #3
		LSL r0, r0, #0x1a
		LSR r0, r0, #0x1e
		LSL r2, r2, #0xa
		BIC r1, r2
		LSL r0, r0, #0xa
		ORR r0, r1
		LDR r1, [pc, #0x74]
		LSR r0, r0, #0xa
		LDRH r1, [r1, #2]
		LSL r0, r0, #0xa
		LSL r1, r1, #0x16
		LSR r1, r1, #0x16
		B        |loc_0800F17C|
|loc_0800F17A|
		B        |loc_0800F274|
|loc_0800F17C|
		ORR r0, r1
		STR r0, [r6, #4]
|loc_0800F180|
		LDRH r0, [r4, #0xc]
		MOV r6, #0
		MOV ip, r6
		MOV lr, r0
		LDR r0, [r4, #0x54]
		LDR r0, [r0]
		CMP r0, #0
		BLE      |loc_0800F274|
		LDR r1, [sp, #0x20]
		MOV r3, #1
		LSL r3, r3, #0xc
		LSL r0, r1, #0x1b
		LSR r0, r0, #2
		ADD r2, r4, #0
		ADD r2, #0xff
		ADD r3, sp
		STR r0, [r3, #0x38]
		ADD r2, #0x61
|loc_0800F1A4|
		LDR r0, [r5]
		MOV r6, ip
		ADD r1, r0, #0
		ADD r0, #8
		STR r0, [r5]
		LSL r3, r6, #1
		ADD r3, r3, r6
		LDR r0, [r4, #0x54]
		LSL r3, r3, #2
		ADD r0, r0, r3
		LDR r3, [sp, #0x24]
		ADD r0, #8
		CMP r3, #0
		BEQ      |loc_0800F24C|
		MOV r6, #3
		LDR r3, [r0, #4]
		LSL r6, r6, #8
		ORR r6, r3
		MOV r3, #0x1f
		LSL r3, r3, #0x19
		BIC r6, r3
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r3, [r3, #0x38]
		ORR r6, r3
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		STR r6, [r1]
		STR r6, [r3, #0x34]
		B        |loc_0800F1FC|
		DCD     0x03001BA8
	INCBIN  baserom.gba_0xf1e8_0xf1f8.extracted
		DCD     0xFE00FFFF
|loc_0800F1FC|
		LDRH r3, [r2, #0x14]
		LDR r6, [r4, #0x6c]
		ADD r6, r6, r3
		MOV r3, #0
		LDRSB r7, [r0, r3]
		LDRB r3, [r0, #2]
		ADD r6, r6, r7
		LSR r3, r3, #1
		SUB r7, r6, r3
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		LDR r6, [r3, #0x34]
		LDR r3, [pc, #0x298]
		AND r6, r3
		LSL r3, r7, #0x17
		LSR r3, r3, #7
		ORR r6, r3
		STR r6, [r1]
		LDRH r3, [r2, #0x16]
		ADD r7, r6, #0
		LDR r6, [r4, #0x70]
		ADD r6, r6, r3
		LDRB r3, [r0, #1]
		ADD r6, r6, r3
		LDRB r3, [r0, #3]
		LSR r3, r3, #1
		SUB r6, r6, r3
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		STR r6, [r3, #0x30]
		LDR r3, [r3, #0x30]
		LSR r6, r7, #8
		LSL r6, r6, #8
		LSL r3, r3, #0x18
		LSR r3, r3, #0x18
		ORR r6, r3
		STR r6, [r1]
		B        |loc_0800F29E|
|loc_0800F24C|
		LDR r6, [r0, #4]
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		STR r6, [r1]
		STR r6, [r3, #0x2c]
		LDRH r3, [r2, #0x14]
		LDR r6, [r4, #0x6c]
		ADD r6, r6, r3
		MOV r3, #0
		LDRSB r7, [r0, r3]
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		ADD r7, r6, r7
		LDR r6, [r3, #0x2c]
		LDR r3, [pc, #0x240]
		AND r6, r3
		LSL r3, r7, #0x17
		B        |loc_0800F276|
|loc_0800F274|
		B        |loc_0800F2E0|
|loc_0800F276|
		LSR r3, r3, #7
		ORR r6, r3
		STR r6, [r1]
		LDRH r3, [r2, #0x16]
		ADD r7, r6, #0
		LDR r6, [r4, #0x70]
		ADD r6, r6, r3
		LDRB r3, [r0, #1]
		ADD r6, r6, r3
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		STR r6, [r3, #0x28]
		LDR r3, [r3, #0x28]
		LSR r6, r7, #8
		LSL r6, r6, #8
		LSL r3, r3, #0x18
		LSR r3, r3, #0x18
		ORR r6, r3
		STR r6, [r1]
|loc_0800F29E|
		LDRB r3, [r4, #8]
		LDR r6, [r1, #4]
		ADD r0, #2
		LSL r7, r3, #0x1a
		MOV r3, #3
		LSL r3, r3, #0xa
		BIC r6, r3
		LSR r3, r7, #0x1e
		LSL r3, r3, #0xa
		ORR r6, r3
		MOV r3, lr
		LSL r3, r3, #0x16
		LSR r6, r6, #0xa
		LSL r6, r6, #0xa
		LSR r3, r3, #0x16
		ORR r6, r3
		STR r6, [r1, #4]
		LDRB r1, [r0]
		LDRB r0, [r0, #1]
		MOV r6, ip
		ADD r6, #1
		MUL r1, r0
		ASR r0, r1, #0x1f
		LSR r0, r0, #0x1b
		ADD r0, r0, r1
		ASR r0, r0, #5
		ADD lr, r0
		LDR r0, [r4, #0x54]
		MOV ip, r6
		LDR r0, [r0]
		CMP r0, r6
		BLE      |loc_0800F2E0|
		B        |loc_0800F1A4|
|loc_0800F2E0|
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_0800F380|
		LDR r0, [r4, #0x64]
		CMP r0, #0
		BEQ      |loc_0800F380|
		LDR r1, [r4, #0x58]
		MOV r3, #0xc
		LDRSB r2, [r1, r3]
		MOV r3, #1
		LDR r0, [r4, #0x6c]
		LSL r3, r3, #0xc
		ADD r3, sp
		ADD r0, r0, r2
		LDR r2, [r3, #0x3c]
		LDRB r1, [r1, #0xd]
		LDR r2, [r2, #4]
		ADD r0, r0, r2
		LDR r2, [r4, #0x70]
		LSL r0, r0, #0x17
		ADD r1, r2, r1
		LDR r2, [r3, #0x3c]
		LSR r0, r0, #7
		LDR r2, [r2, #8]
		ADD r2, r1, r2
		LDR r1, [r5]
		LSL r2, r2, #0x18
		ADD r6, r1, #0
		ADD r6, #8
		STR r6, [r5]
		LDR r3, [r4, #0x5c]
		LSR r2, r2, #0x18
		LDR r5, [r3, #0xc]
		LDR r3, [pc, #0x18c]
		AND r5, r3
		ORR r0, r5
		LSR r0, r0, #8
		LSL r0, r0, #8
		ORR r0, r2
		STR r0, [r1]
		LDRB r2, [r4, #8]
		LDR r5, [r1, #4]
		MOV r3, #3
		LSL r2, r2, #0x1a
		LSR r2, r2, #0x1e
		LSL r3, r3, #0xa
		BIC r5, r3
		LSL r2, r2, #0xa
		ORR r2, r5
		STR r2, [r1, #4]
		LDR r5, [r4, #0x5c]
		LSR r2, r2, #0xa
		LDR r3, [r5, #8]
		LSL r2, r2, #0xa
		LDRH r5, [r3, #2]
		LSL r3, r5, #0x16
		LSR r3, r3, #0x16
		ORR r2, r3
		MOV r3, #0xf
		LSL r3, r3, #0xc
		BIC r2, r3
		MOV r3, #1
		LSL r3, r3, #0xc
		ADD r3, sp
		STR r2, [r1, #4]
		LDR r2, [r3, #0x40]
		LDR r2, [r2, #0x10]
		CMP r2, #0
		BEQ      |loc_0800F380|
		MOV r2, #0xff
		ADD r2, #1
		ORR r0, r2
		MOV r2, #0x1f
		LSL r2, r2, #0x19
		BIC r0, r2
		LDR r2, [sp, #0x20]
		LSL r2, r2, #0x1b
		LSR r2, r2, #2
		ORR r0, r2
		STR r0, [r1]
|loc_0800F380|
		LDR r0, [r4, #0x54]
		LDR r1, [r4, #0x30]
		CMP r1, r0
		BNE      |loc_0800F38C|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xee72
|loc_0800F38C|
		STR r0, [r4, #0x30]
		LDRB r2, [r0, #6]
		LDRB r1, [r0, #7]
		MUL r2, r1
		STR r2, [r4, #0x48]
		LDR r1, [r4, #0x34]
		CMP r1, #0
		BNE      |loc_0800F3B4|
		LDR r1, [r0]
		CMP r1, #1
		BNE      |loc_0800F3B4|
		LDR r1, [r0, #0x10]
		LDR r2, [r1]
		CMP r2, #0
		BNE      |loc_0800F3B4|
		ADD r0, r1, #0
		ADD r0, #8
		STR r0, [r4, #0x44]
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0xee72
|loc_0800F3B4|
		LDR r6, [r4, #0x40]
		MOV r5, #0
		STR r6, [r4, #0x44]
		LDR r0, [r0]
		CMP r0, #0
		BLE      |loc_0800F3F4|
|loc_0800F3C0|
		LSL r1, r5, #1
		ADD r1, r1, r5
		LDR r0, [r4, #0x54]
		LSL r1, r1, #2
		ADD r7, r0, r1
		ADD r7, #8
		LDR r2, [r4, #0x34]
		LDR r0, [r7, #8]
		ADD r1, sp, #0x28
		BL       |sub_0803D966|
		ADD r0, r7, #2
		LDRB r7, [r7, #2]
		LDRB r0, [r0, #1]
		ADD r1, sp, #0x28
		MUL r7, r0
		ADD r2, r7, #0
		ADD r0, r6, #0
		BL       |Thunk_VramCopy|
		LDR r0, [r4, #0x54]
		ADD r6, r6, r7
		LDR r0, [r0]
		ADD r5, #1
		CMP r0, r5
		BGT      |loc_0800F3C0|
|loc_0800F3F4|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0xee72
