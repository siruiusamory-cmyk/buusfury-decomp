	CODE16
|sub_08006EE8|
|unk_08006EE8|
; cited by 0x08006E3E (a pc-relative load targets 0x08006FE0)
		LDR r4, [pc, #0xf4]
		LDR r2, [r4]
		LDRH r2, [r2, #4]
		LSL r2, r2, #0x1c
		LSR r2, r2, #0x1f
		BEQ      |loc_08006FDA|
		LDR r2, [r4, #0xc]
		MOV r3, #0x68
		LDRB r6, [r2]
		MUL r3, r6
		ADD r2, r3, r2
		MOV r3, #0x9f
		LSL r3, r3, #3
		ADD r2, r2, r3
		ADD r2, #0x16
		MOV r3, #0
		LDRSH r2, [r2, r3]
		CMP r2, #0
		BEQ      |loc_08006FDA|
		MOV r6, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0xc]
		LDRB r0, [r0]
		CMP r0, #8
		BNE      |loc_08006F56|
		LDR r1, [pc, #0xbc]
		ADD r1, #0x18
		MOV r0, #0x27
		BL       |sub_0802BFBC|
		ADD r5, r0, #0
		ADD r1, r0, #0
		LDR r0, [r4, #0x14]
		BL       |List_Append|
		MOV r0, #4
		DCW     0xF036
		DCW     0xFB3F
		CMP r0, #0
		BEQ      |loc_08006F42|
		LDR r1, [pc, #0xc0]
		STR r1, [r0]
|loc_08006F42|
		BL       |inc_0x03d784_0x041118| + 0x11c
		LDR r0, [r4, #0x14]
		BL       |loc_08011E94|
		ADD r1, r5, #0
		LDR r0, [r4, #0x14]
		BL       |loc_08011944|
		B        |loc_08006FDA|
|loc_08006F56|
		MOV r0, #0xc
		DCD     0xFB2EF036
		CMP r0, #0
		BEQ      |loc_08006F6C|
		MOV r1, #0xff
		ADD r1, #1
		STR r1, [r0, #4]
		LDR r1, [pc, #0x88]
		STR r5, [r0, #8]
		STR r1, [r0]
|loc_08006F6C|
		BL       |inc_0x03d784_0x041118| + 0x11c
		LDR r0, [r4, #0x14]
		BL       |loc_08011DB4|
		MOV r0, #0xff
		ADD r0, #0x59
		DCW     0xF036
		DCW     0xFB1D
		CMP r0, #0
		BEQ      |loc_08006FA6|
		LDR r1, [pc, #0x80]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		STR r6, [r1, #0x14]
		STR r6, [r1, #0x18]
		STR r6, [r1, #0x20]
		STR r6, [r1, #0x24]
		MOV r1, #0xff
		ADD r1, #0x55
		STR r6, [r1, r0]
		LDR r1, [pc, #0x64]
		STR r1, [r0]
|loc_08006FA6|
		BL       |inc_0x03d784_0x041118| + 0x11c
		LDR r0, [r4, #0x14]
		BL       |loc_08011E0E|
		MOV r1, #1
		LDR r0, [r4, #8]
		BL       |loc_0800938C|
		MOV r2, #0
		MOV r1, #0x1a
		LDR r0, [r4, #0x14]
		BL       |loc_08011C0C|
		MOV r0, #0xc
		DCD     0xFAF8F036
		CMP r0, #0
		BEQ      |loc_08006FD4|
		LDR r1, [pc, #0x2c]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		STR r5, [r0, #8]
|loc_08006FD4|
		BL       |inc_0x03d784_0x041118| + 0x11c
		B        |loc_08006FDC|
|loc_08006FDA|
		B        |loc_08006FDC|
|loc_08006FDC|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x6d8e
		DCD     0x08070180
		DCD     0x03001C34
		DCD     0x000005C4
		DCD     0x08319488
		DCD     0x0804A920
	INCBIN  baserom.gba_0x6ff4_0x6ffa.extracted
