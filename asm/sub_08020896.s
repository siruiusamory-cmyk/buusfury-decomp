	CODE16
|sub_08020896|
|unk_08020896|
		LDR r1, [r4, #0x18]
		ADD r1, #1
		STR r1, [r4, #0x18]
		CMP r1, #4
		DCW     0xDBF8
		LSL r1, r1, #0x1d
		LSR r1, r1, #0x1f
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r4, #0x4c]
		LSL r1, r1, #2
		ADD r1, r0, r1
		ADD r1, #0xc
		STR r1, [r4, #0x48]
		LDR r0, [r4, #0x44]
		CMP r1, r0
		DCW     0xD0EC
		STR r1, [r4, #0x44]
		LDRB r2, [r1, #2]
		LDRB r0, [r1, #3]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		BL       |Thunk_VramCopy|
		DCW     0xE7E1
|loc_080208CE|
|unk_080208CE|
		LDR r1, [pc, #0x1ac]
		LDR r1, [r1, #8]
		ADD r6, r1, #0
		ADD r6, #0x18
		ADD r1, #0x80
		CMP r0, #0
		LDR r0, [r4, #0x38]
		LDR r2, [r4, #0x30]
		DCW     0xD072
		LDR r3, [r4, #0x34]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x40]
		ADD r2, r3, #0
		STR r3, [sp, #0x44]
		LDR r3, [r4, #0x20]
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x40]
		ADD r2, r3, r2
		STR r2, [sp, #0x44]
		STR r2, [sp, #0x4c]
		STR r0, [sp, #0x48]
		LDR r0, [r4, #0x50]
		ADD r3, sp, #0x20
		STR r0, [sp, #0x34]
		LDR r0, [r4, #0x3c]
		ADD r2, sp, #0x14
		STRB r0, [r3, #8]
		LDR r0, [r4, #0x40]
		LDR r3, [pc, #0x190]
		LDRB r0, [r0, #6]
		ADD r7, r2, #4
		LSL r0, r0, #3
		ADD r0, r0, r3
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x40]
		ADD r3, sp, #0
		LDRH r0, [r0, #2]
		STR r0, [sp, #0x2c]
		LDR r0, [r4, #0x50]
		ADD r0, #0xff
		ADD r0, #0xc1
		LDR r0, [r0, #0x10]
		STRB r0, [r3, #0x14]
		LDR r3, [sp, #0x48]
		LDR r0, [sp, #0x48]
		SUB r3, #8
		MOV ip, r3
		LDR r3, [sp, #0x4c]
		LDR r2, [sp, #0x4c]
		SUB r3, #8
		MOV lr, r3
		MOV r3, ip
		STR r3, [sp, #0x18]
		ADD r0, #8
		ADD r2, #8
		MOV r3, lr
		STR r4, [sp, #0x44]
		DCW     0xE000
|loc_08020948|
|unk_08020948|
; cited by 0x080206D6 (a pc-relative load targets 0x08020A78)
		B        |loc_08020B62|
		STR r0, [sp, #0x20]
		STR r3, [sp, #0x1c]
		STR r2, [sp, #0x24]
		LDR r1, [r1, #0x2c]
		ADD r0, r7, #0
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_08020A36|
		LDR r0, [pc, #0x11c]
		ADD r2, sp, #0x14
		MOV r1, #0
		LDR r0, [r0, #4]
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_08020A38|
		LDR r0, [r4, #0x30]
		LDR r1, [r4, #0x34]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #8]
		LDR r2, [sp, #0x48]
		STR r0, [sp, #4]
		ADD r0, r2, r0
		LDR r2, [sp, #0x4c]
		STR r0, [sp, #0xc]
		ADD r1, r2, r1
		STR r1, [sp, #8]
		STR r1, [sp, #0x10]
		STR r0, [sp, #4]
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020996|
		LDR r0, [pc, #0xec]
		LDR r0, [r0, #4]
		BL       |loc_080116FC|
|loc_08020996|
		LDR r0, [pc, #0xec]
		LDR r6, [r0, #4]
		LDR r0, [r4, #0x14]
		SUB r0, r6, r0
		CMP r0, #0
		BLE      |loc_08020A26|
		MOV r0, #5
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, r6, r0
		ADD r0, #3
		STR r0, [r4, #0x14]
		LDR r7, [pc, #0xcc]
		MOV r0, #2
		LDR r6, [r7]
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0xcc]
		LSL r0, r0, #2
		SUB r1, #0x24
		B        |loc_080209C8|
		B        |loc_08020AFC|
|loc_080209C8|
		ADD r1, r0, r1
		LDR r0, [pc, #0xc4]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r7, #4]
		BL       |loc_080116FC|
		MOV r6, #1
		LSL r6, r6, #0xa
		CMP r0, r6
		BLE      |loc_08020A26|
		MOV r0, #0x20
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [sp, #0xc]
		ADD r0, r0, r1
		SUB r0, #0x10
		STR r0, [sp, #0xc]
		MOV r0, #0x20
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [sp, #0x10]
		ADD r0, r0, r1
		SUB r0, #0x10
		STR r0, [sp, #0x10]
		LSL r0, r6, #4
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSL r1, r6, #2
		ADD r0, r0, r1
		MOV r2, #0x38
		STR r2, [sp, #8]
		STR r0, [sp]
		MOV r3, #4
		MOV r0, #0
		LDR r2, [pc, #0x8c]
		ADD r1, sp, #0xc
		STR r6, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r7, #4]
		BL       |List_Append|
|loc_08020A26|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020A64|
		MOV r0, #1
		STRB r0, [r4, #0x11]
		NEG r0, r0
		STR r0, [r4, #0x1c]
		B        |loc_08020A64|
|loc_08020A36|
		B        |loc_08020A56|
|loc_08020A38|
		B        |loc_08020A3A|
|loc_08020A3A|
		LDR r0, [pc, #0x6c]
		LDR r0, [r0]
		CMP r0, #0
		BNE      |loc_08020A4E|
		ADD r0, r6, #0
		ADD r1, r7, #0
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08020A64|
|loc_08020A4E|
		LDR r0, [r4, #0x38]
		ADD r0, #3
		STR r0, [r4, #0x38]
		B        |loc_08020A64|
|loc_08020A56|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020A64|
		MOV r0, #1
		STRB r0, [r4, #0x11]
		NEG r0, r0
		STR r0, [r4, #0x1c]
|loc_08020A64|
		LDR r0, [sp, #0x48]
		LDR r2, [r4, #0x20]
		ADD r1, r4, #0
		ADD r1, #0x20
		CMP r0, r2
		ADD r6, sp, #0x48
		BGE      |loc_08020AAC|
		ADD r0, r6, #0
		B        |loc_08020AAE|
	INCBIN  baserom.gba_0x20a76_0x20a7c.extracted
		DCD     0x08725048
		DCD     0x0804AEF8
		DCD     0x03000F90
		DCD     VRAM + 0x10000
		DCD     0x083192CC
		DCD     0x000005C4
	INCBIN  baserom.gba_0x20a94_0x20aa4.extracted
		DCD     0x08712FDC
		DCD     0x03002C04
|loc_08020AAC|
		ADD r0, r1, #0
|loc_08020AAE|
		LDR r0, [r0]
		LDR r3, [sp, #0x4c]
		SUB r0, #6
		STR r0, [sp, #0x18]
		ADD r0, r4, #0
		LDR r7, [r4, #0x24]
		ADD r0, #0x24
		ADD r2, r6, #4
		CMP r3, r7
		BGE      |loc_08020AC6|
		ADD r3, r2, #0
		B        |loc_08020AC8|
|loc_08020AC6|
		ADD r3, r0, #0
|loc_08020AC8|
		LDR r3, [r3]
		SUB r3, #6
		STR r3, [sp, #0x1c]
		LDR r3, [sp, #0x48]
		LDR r7, [r1]
		CMP r3, r7
		BLE      |loc_08020AD8|
		ADD r1, r6, #0
|loc_08020AD8|
		LDR r1, [r1]
		ADD r1, #6
		STR r1, [sp, #0x20]
		LDR r1, [sp, #0x4c]
		LDR r3, [r0]
		CMP r1, r3
		BLE      |loc_08020AE8|
		ADD r0, r2, #0
|loc_08020AE8|
		LDR r0, [r0]
		ADD r2, sp, #0x14
		ADD r0, #6
		STR r0, [sp, #0x24]
		LDR r0, [pc, #0x2ac]
		MOV r1, #0
		LDR r0, [r0, #4]
		BL       |loc_08011C0C|
		B        |loc_08020B62|
|loc_08020AFC|
		LDR r3, [r4, #0x34]
		MUL r2, r0
		MUL r3, r0
		ADD r0, r2, #0
		STR r2, [sp, #0x48]
		ADD r2, r3, #0
		STR r3, [sp, #0x4c]
		LDR r3, [r4, #0x20]
		ADD r0, r3, r0
		LDR r3, [r4, #0x24]
		STR r0, [sp, #0x48]
		ADD r2, r3, r2
		ADD r7, r2, #0
		ADD r3, r0, #0
		SUB r7, #8
		STR r2, [sp, #0x4c]
		ADD r2, #8
		STR r7, [sp, #0x44]
		SUB r3, #8
		ADD r0, #8
		STR r0, [sp, #0x48]
		STR r3, [sp, #0x40]
		ADD r7, sp, #0x40
		STR r2, [sp, #0x4c]
		LDR r1, [r1, #0x2c]
		ADD r0, r7, #0
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_08020B54|
		LDR r0, [pc, #0x268]
		LDR r0, [r0]
		CMP r0, #0
		BNE      |loc_08020B4C|
		ADD r0, r6, #0
		ADD r1, r7, #0
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08020B62|
|loc_08020B4C|
		LDR r0, [r4, #0x38]
		ADD r0, #3
		STR r0, [r4, #0x38]
		B        |loc_08020B62|
|loc_08020B54|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		BNE      |loc_08020B62|
		MOV r0, #1
		STRB r0, [r4, #0x11]
		NEG r0, r0
		STR r0, [r4, #0x1c]
