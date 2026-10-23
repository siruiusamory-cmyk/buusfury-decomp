	CODE16
|sub_08037682|
|unk_08037682|
		LDR r0, [r4, #0x54]
		ADD r0, #1
		STR r0, [r4, #0x54]
		CMP r0, #0x10
		BGE      |loc_08037698|
		ASR r1, r0, #3
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		ADD r0, r1, r0
		STR r0, [r4, #0x58]
		B        |loc_080376AC|
|loc_08037698|
		CMP r0, #0x10
		BNE      |loc_080376A0|
		MOV r0, #0x60
		STR r0, [r4, #0x54]
|loc_080376A0|
		LDR r0, [r4, #0x54]
		ASR r1, r0, #5
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1f
		ADD r0, r1, r0
		STR r0, [r4, #0x58]
|loc_080376AC|
		LDR r0, [r4, #0x4c]
		LDR r1, [r4, #0x58]
		LDR r5, [r0]
		CMP r1, r5
		BLT      |loc_0803774E|
		LDR r0, [r0, #4]
		SUB r0, r0, r5
		BNE      |loc_080376C0|
		STR r5, [r4, #0x58]
		B        |loc_0803774E|
|loc_080376C0|
		LDR r1, [r4, #0x54]
		ASR r1, r1, #2
		BL       |Thunk_SignedDivide|
		ADD r0, r1, r5
		STR r0, [r4, #0x58]
		B        |loc_0803774E|
|loc_080376CE|
|unk_080376CE|
		LDR r0, [r4, #0x4c]
		ADD r1, r0, #0
		LDR r0, [r0, #4]
		LDR r5, [r1]
		SUB r0, r0, r5
		BEQ      |loc_080376EC|
		LDR r1, [r4, #0x58]
		CMP r1, r5
		BLT      |loc_080376EC|
		LDR r1, [r4, #0x54]
		ASR r1, r1, #2
		BL       |Thunk_SignedDivide|
		ADD r0, r1, r5
		STR r0, [r4, #0x58]
|loc_080376EC|
		LDR r1, [r4, #0x20]
		LDR r2, [r4, #0x44]
		ADD r1, r1, r2
		STR r1, [r4, #0x20]
		LDR r0, [r4, #0x48]
		LDR r1, [r4, #0x24]
		ADD r0, r1, r0
		STR r0, [r4, #0x24]
		LDR r0, [r4, #0x54]
		ADD r0, #1
		STR r0, [r4, #0x54]
		ADD r0, sp, #0x38
		ADD r1, r6, #0
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r1, [pc, #0x174]
		LDR r0, [sp, #0x38]
		ADD r1, #0xc
		LDR r2, [r1]
		SUB r2, r0, r2
		LDR r0, [sp, #0x3c]
		LDR r3, [r1, #4]
		STR r2, [sp, #0x30]
		SUB r0, r0, r3
		STR r0, [sp, #0x34]
		STR r0, [sp, #0x44]
		LDR r0, [sp, #0x38]
		STR r2, [sp, #0x40]
		LDR r2, [r1]
		ADD r0, r0, r2
		LDR r2, [sp, #0x3c]
		LDR r1, [r1, #4]
		STR r0, [sp, #0x30]
		ADD r1, r2, r1
		STR r1, [sp, #0x34]
		STR r1, [sp, #0x4c]
		STR r0, [sp, #0x48]
		LDR r0, [r7, #8]
		ADD r0, #0x80
		LDR r1, [r0, #0x2c]
		ADD r0, sp, #0x40
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_0803774E|
		ADD r0, r4, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x23ae
		B        |inc_0x351c0_0x3d4d0| + 0x24be
|loc_0803774E|
|unk_0803774E|
		B        |inc_0x351c0_0x3d4d0| + 0x25d4
|loc_08037750|
|unk_08037750|
; cited by 0x080374A8 (a pc-relative load targets 0x08037878)
		B        |loc_08037752|
|loc_08037752|
		LSL r0, r0, #0x1d
		BNE      |inc_0x351c0_0x3d4d0| + 0x24be
		LDR r0, [r7, #4]
		BL       |loc_080116FC|
		MOV r1, #1
		LSL r1, r1, #0xa
		CMP r0, r1
		BLT      |inc_0x351c0_0x3d4d0| + 0x24be
		LDR r0, [r4, #0x6c]
		LSL r0, r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x64]
		ADD r0, r0, r1
		STR r0, [sp, #0x48]
		LDR r0, [r4, #0x6c]
		LSL r0, r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x68]
		MOV r2, #0x38
		ADD r0, r0, r1
		STR r0, [sp, #0x4c]
		MOV r0, #0
		ADD r1, sp, #0x48
		BL       |loc_0801952C|
		ADD r1, r0, #0
		LDR r0, [r7, #4]
		BL       |List_Append|
		B        |inc_0x351c0_0x3d4d0| + 0x24be
		LDR r1, [r4, #0x58]
		LDR r0, [r4, #0x50]
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x478a
		CMP r0, #0
		BNE      |loc_080377BC|
		ADD r1, r4, #0
		LDR r0, [r7, #4]
		BL       |loc_08011944|
		B        |inc_0x351c0_0x3d4d0| + 0x24be
|loc_080377BC|
		LDR r0, [sp, #0x50]
		LDRB r0, [r0]
		CMP r0, #1
		BNE      |inc_0x351c0_0x3d4d0| + 0x258c
		LDR r0, [sp, #0x58]
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x258c
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x258c
		LDR r0, [r4, #0x54]
		LSL r0, r0, #0x1e
		BNE      |inc_0x351c0_0x3d4d0| + 0x258c
		ADD r1, r6, #0
		ADD r0, sp, #0x48
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r0, sp, #0x40
		MOV r1, #0
		MOV r2, #0
		STMIA r0!, {r1, r2}
		LDR r0, [r4, #0x58]
		LDR r1, [pc, #0x94]
		LSL r0, r0, #2
		ADD r1, #0x14
		LDR r0, [r1, r0]
		ADD r3, sp, #0x20
		STR r0, [sp, #0x40]
		LDR r0, [r4, #0x58]
		ADD r2, sp, #0xc
		LSL r0, r0, #2
		LDR r0, [r1, r0]
		STR r0, [sp, #0x44]
		LDR r0, [r4, #0x1c]
		STR r0, [sp, #0x2c]
		LDRB r0, [r4, #0x10]
		STRB r0, [r3]
		LDR r0, [pc, #0x94]
		STR r0, [sp, #0x28]
		LDR r1, [r4, #0x4c]
		LDR r0, [r4, #0x60]
		LDR r1, [r1, #0xc]
		MUL r0, r1
		LDR r1, [pc, #0x80]
		ADD r0, r0, r1
		ASR r0, r0, #0x10
		STR r0, [sp, #0x24]
		LDR r0, [sp, #0x48]
		LDR r1, [sp, #0x40]
		LDR r3, [sp, #0x44]
		SUB r1, r0, r1
		LDR r0, [sp, #0x4c]
		STR r1, [sp, #4]
		SUB r0, r0, r3
		STR r0, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x10]
		LDR r1, [sp, #0x40]
		LDR r0, [sp, #0x48]
		ADD r1, r0, r1
		LDR r0, [sp, #0x4c]
		STR r1, [sp, #4]
		ADD r0, r0, r3
		STR r0, [sp, #8]
		STR r0, [sp, #0x1c]
		STR r1, [sp, #0x18]
		LDRB r0, [r4, #0x11]
		ADD r3, sp, #0
		MOV r1, #0
		STRB r0, [r3, #0xc]
		STR r4, [sp, #0x3c]
		LDR r0, [r7, #4]
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x25d2
		MOV r0, #2
		LDR r4, [r7]
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		LDR r1, [pc, #0x20]
		ADD r0, r3, r0
		LSL r0, r0, #2
		SUB r1, #0x24
		ADD r1, r0, r1
		LDR r0, [pc, #0x1c]
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r4, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		B        |inc_0x351c0_0x3d4d0| + 0x24be
		DCD     0x0804A26C
		DCD     0x0807268C
		DCD     0x0876ACF0
		DCD     0x083192CC
		DCD     0x000005C4
		DCD     0x03003284
		DCD     0x08049680
		DCD     0x0000FFFF
	INCBIN  baserom.gba_0x37898_0x3789a.extracted
|sub_0803789A|
	DCW      0x0804
	DCW      0x80f0
	DCW      0x086b
