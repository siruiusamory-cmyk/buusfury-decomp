	CODE16
|sub_0802333E|
|unk_0802333E|
; cited by 0x080230A0 (a pc-relative load targets 0x08023484)
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCW     0xF01A
		DCW     0xF939
		ADD r4, r0, #0
		BEQ      |loc_08023364|
		MOV r5, #1
		ADD r3, r5, #0
		MOV r2, #0xd
		MOV r1, #0x5e
		ADD r0, r4, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0x164]
		STR r0, [r4]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r4, r0
		STR r5, [r0, #0x38]
|loc_08023364|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7E6
|loc_0802336E|
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [pc, #0x10c]
		LDR r0, [r0, #0x10]
		LDRB r0, [r0]
		CMP r0, #1
		BNE      |loc_08023464|
		LDR r0, [r7, #0x1c]
		BL       |loc_08011B04|
		LDR r0, [r7, #0x1c]
		BL       |loc_080115B0|
		LDR r0, [r7, #0x1c]
		BL       |List_ReleaseAll2|
		MOV r2, #1
		LSL r2, r2, #0x1a
		LDRH r0, [r2]
		LSR r1, r2, #0x12
		BIC r0, r1
		STRH r0, [r2]
		LDR r2, [r4, #0x1c]
		MOV r0, #0xff
		ADD r0, #0x31
		STR r2, [sp]
		DCW     0xF01A
		DCW     0xF907
		CMP r0, #0
		BEQ      |loc_080233D8|
		LDR r1, [pc, #0x108]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		B        |loc_080233BE|
		B        |loc_08023616|
|loc_080233BE|
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		MOV r2, #0xff
		ADD r2, #0x15
		STR r6, [r1, #0x10]
		STRB r6, [r2, r0]
		LDR r2, [pc, #0xf8]
		STR r2, [r0]
		MOV r2, #1
		STR r2, [r1, #0x28]
		STR r6, [r1, #0x1c]
		LDR r2, [sp]
		STR r2, [r1, #0x18]
|loc_080233D8|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		BNE      |loc_08023464|
		LDR r0, [pc, #0xe4]
		LDR r0, [r0]
		STR r0, [r4, #0x20]
		LDR r0, [r7, #0xc]
		BL       |Object_SubtractDelta1|
		LDR r0, [r4, #0x1c]
		LDR r1, [pc, #0x94]
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #2
		ADD r1, #0x24
		ADD r0, r0, r1
		LDR r1, [r7, #0x14]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6512
		LDR r0, [r4, #0x20]
		LDR r1, [pc, #0x80]
		LSL r3, r0, #3
		SUB r0, r3, r0
		LSL r0, r0, #2
		ADD r1, #0x24
		ADD r0, r0, r1
		LDR r1, [r7, #0x18]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6512
		LDR r0, [r7, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0x14]
		LDR r1, [pc, #0xa4]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
		BL       |inc_0x03d784_0x041118| + 0x2a3e
		LDR r0, [pc, #0x94]
		DCW     0xF01A
		DCW     0xF8BD
		ADD r4, r0, #0
		BEQ      |loc_08023456|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x22ba
		LDR r0, [pc, #0x88]
		MOV r1, #0x10
		STR r0, [r4]
		LSL r0, r1, #6
		ADD r0, r4, r0
		STR r1, [r0, #8]
		STR r6, [r0, #4]
|loc_08023456|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x11c
		MOV r0, #0xc
		DCW     0xF01A
		DCW     0xF8AB
		B        |loc_08023466|
|loc_08023464|
		DCW     0xE045
|loc_08023466|
		CMP r0, #0
		BEQ      |loc_0802346E|
		LDR r1, [pc, #0x6c]
		STR r1, [r0]
|loc_0802346E|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #1
		BNE      |loc_080234EE|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7500
		BL       |inc_0x03d784_0x041118| + 0x29dc
		B        |loc_080234DC|
	INCBIN  baserom.gba_0x23482_0x23484.extracted
		DCD     0x0872BFA8
		DCD     0x00000584
		DCD     0x0806BCE8
|loc_08023490|
|unk_08023490|
; cited by 0x08023148 (a pc-relative load targets 0x08023498)
	INCBIN  baserom.gba_0x23490_0x234dc.extracted
|loc_080234DC|
		ADD r0, r5, #0
		BL       |loc_08022AF6|
		ADD r0, r5, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6dbc
		LDR r0, [r7, #0x20]
		BL       |inc_0x03d784_0x041118| + 0x2a16
|loc_080234EE|
		MOV r0, #0
		DCW     0xE724
		LDR r0, [r7, #0x10]
		LDRB r0, [r0]
		CMP r0, #0
		BNE      |loc_080235DE|
		LDR r0, [r7, #0x1c]
		BL       |loc_08011B04|
		LDR r0, [r7, #0x1c]
		BL       |loc_080115B0|
		LDR r0, [r7, #0x1c]
		BL       |List_ReleaseAll2|
		MOV r2, #1
		LSL r2, r2, #0x1a
		LDRH r0, [r2]
		LSR r1, r2, #0x12
		BIC r0, r1
		STRH r0, [r2]
		LDR r1, [r4, #0x1c]
		LDR r0, [pc, #0x288]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r5, r0
		ADD r0, r1, r0
		LDR r0, [r0, #0xc]
		MOV r3, #0x68
		MUL r0, r3
		LDR r1, [pc, #0x278]
		ADD r0, r0, r5
		ADD r1, r0, r1
		LDR r0, [r7, #0x14]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6542
		LDR r2, [r7, #0x14]
		MOV r0, #0xff
		STR r2, [sp]
		LDR r4, [r7, #0x18]
		ADD r0, #0x31
		DCW     0xF01A
		DCW     0xF839
		CMP r0, #0
		BEQ      |loc_08023570|
		LDR r1, [pc, #0x260]
		MOV r2, #0xff
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		ADD r2, #0x15
		STRB r6, [r2, r0]
		LDR r2, [pc, #0x24c]
		STR r2, [r0]
		STR r6, [r1, #0x28]
		STR r6, [r1, #0x1c]
		LDR r2, [sp]
		ADD r1, #0x20
		STMIA r1!, {r2, r4}
|loc_08023570|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		BNE      |loc_080235DE|
		LDR r0, [r7, #0xc]
		BL       |Object_SubtractDelta1|
		LDR r0, [r7, #0xc]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0x14]
		LDR r1, [pc, #0x220]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
		BL       |inc_0x03d784_0x041118| + 0x2a3e
		LDR r0, [pc, #0x214]
		DCD     0xF808F01A
		ADD r4, r0, #0
		BEQ      |loc_080235C0|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x22ba
		LDR r0, [pc, #0x208]
		MOV r1, #0x10
		STR r0, [r4]
		LSL r0, r1, #6
		ADD r0, r4, r0
		STR r1, [r0, #8]
		STR r6, [r0, #4]
|loc_080235C0|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x11c
		MOV r0, #0xc
		DCD     0xFFF6F019
		CMP r0, #0
		BEQ      |loc_080235D4|
		LDR r1, [pc, #0x1ec]
		STR r1, [r0]
|loc_080235D4|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #1
		BNE      |loc_080235FC|
		B        |loc_080235E0|
|loc_080235DE|
		B        |loc_08023600|
|loc_080235E0|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7500
		BL       |inc_0x03d784_0x041118| + 0x29dc
		ADD r0, r5, #0
		BL       |loc_08022AF6|
		ADD r0, r5, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x6dbc
		LDR r0, [r7, #0x20]
		BL       |inc_0x03d784_0x041118| + 0x2a16
|loc_080235FC|
		MOV r0, #0
		DCW     0xE69D
|loc_08023600|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7500
		BL       |inc_0x03d784_0x041118| + 0x29dc
		ADD r0, r5, #0
		BL       |loc_08022AF6|
		LDR r0, [r7, #0x20]
		BL       |inc_0x03d784_0x041118| + 0x2a16
|loc_08023616|
		MOV r0, #0
		DCW     0xE690
