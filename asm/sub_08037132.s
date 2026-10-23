	CODE16
|sub_08037132|
|unk_08037132|
		MOV r2, #0xff
		LDR r0, [r4, #0x18]
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_08037140|
		ADD r0, #0x20
		STR r0, [r4, #0x18]
|loc_08037140|
|unk_08037140|
; cited by 0x08036F76 (a pc-relative load targets 0x08037230)
		CMP r1, #0
		BEQ      |loc_0803712E|
		LDR r0, [r4, #0x34]
		LDR r1, [r4, #0x2c]
		LDR r2, [r4, #0x30]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r1, [sp, #0x2c]
		ADD r1, r2, #0
		STR r2, [sp, #0x30]
		LDR r2, [r4, #0x1c]
		ADD r3, sp, #0
		ADD r0, r2, r0
		LDR r2, [r4, #0x20]
		STR r0, [sp, #0x2c]
		ADD r1, r2, r1
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x38]
		STR r0, [sp, #0x34]
		LDR r0, [r4, #0x40]
		LDR r1, [r4, #0x18]
		LDR r0, [r0, #4]
		ADD r2, r4, #0
		MUL r0, r1
		LDR r1, [r4, #0x44]
		ASR r0, r0, #8
		STR r1, [sp, #0x20]
		LDR r1, [r4, #0x38]
		ADD r2, #0x1c
		STRB r1, [r3, #0x14]
		LDR r1, [pc, #0xdc]
		ADD r6, sp, #0x34
		STR r1, [sp, #0x1c]
		LDR r1, [r4, #0x40]
		LDR r1, [r1, #8]
		STR r1, [sp, #0x18]
		LDR r1, [r4, #0x44]
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r1, [r1, #0x10]
		STRB r1, [r3]
		STR r4, [sp, #0x30]
		LDR r1, [sp, #0x34]
		LDR r3, [r4, #0x1c]
		CMP r1, r3
		BGE      |loc_080371A2|
		ADD r1, r6, #0
		B        |loc_080371A4|
|loc_080371A2|
		ADD r1, r2, #0
|loc_080371A4|
		LDR r1, [r1]
		LDR r5, [sp, #0x38]
		SUB r1, r1, r0
		STR r1, [sp, #4]
		ADD r1, r4, #0
		LDR r7, [r4, #0x20]
		ADD r1, #0x20
		ADD r3, r6, #4
		CMP r5, r7
		BGE      |loc_080371BC|
		ADD r5, r3, #0
		B        |loc_080371BE|
|loc_080371BC|
		ADD r5, r1, #0
|loc_080371BE|
		LDR r5, [r5]
		SUB r5, r5, r0
		STR r5, [sp, #8]
		LDR r5, [sp, #0x34]
		LDR r7, [r2]
		CMP r5, r7
		BLE      |loc_080371CE|
		ADD r2, r6, #0
|loc_080371CE|
		LDR r2, [r2]
		ADD r2, r2, r0
		STR r2, [sp, #0xc]
		LDR r2, [sp, #0x38]
		LDR r5, [r1]
		CMP r2, r5
		BLE      |loc_080371DE|
		ADD r1, r3, #0
|loc_080371DE|
		LDR r1, [r1]
		LDR r6, [pc, #0x54]
		ADD r0, r1, r0
		STR r0, [sp, #0x10]
		LDR r0, [r6, #4]
		MOV r1, #0
		MOV r2, sp
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_0803712E|
		LDR r0, [pc, #0x50]
		LDR r5, [r0, #4]
		LDR r0, [r4, #0x14]
		SUB r0, r5, r0
		CMP r0, #0
		BLE      |loc_0803712E|
		MOV r0, #5
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, r5, r0
		ADD r0, #3
		STR r0, [r4, #0x14]
		LDR r4, [r6]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x44]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x2c]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r4, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		B        |loc_0803712E|
	INCBIN  baserom.gba_0x3722e_0x37238.extracted
		DCD     0x0875F808
		DCD     0x0804AF24
		DCD     0x0807268C
		DCD     0x0876174C
		DCD     0x03000F90
		DCD     0x08319428
		DCD     0x000005C4
	INCBIN  baserom.gba_0x37254_0x3725a.extracted
|sub_0803725A|
	DCW      0x0804
	DCW      0x80e0
	DCW      0x086b
	DCW      0x92a8
	DCW      0x0831
