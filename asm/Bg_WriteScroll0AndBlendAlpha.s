|Bg_WriteScroll0AndBlendAlpha|
	CODE16
|unk_08030C2E|
; cited by 0x08030B2E (a pc-relative load targets 0x08030EF4)
		LDR r0, [pc, #0x2dc]
		ADD r1, r6, #0
		STR r0, [r6]
		LDR r0, [pc, #0x2d8]
		ADD r1, #0xc
		STR r1, [sp, #0x60]
		STR r0, [r6, #0xc]
		LDR r0, [pc, #0x2d4]
		STR r0, [r6]
		ADD r0, #0x2c
		STR r0, [r6, #0xc]
		ADD r2, r1, #4
		STR r2, [sp, #0x5c]
		MOV r0, #0
		STR r0, [r6, #0x10]
		MOV r2, #1
		LSL r2, r2, #0xb
		STR r0, [r6, #0x54]
		LDR r0, [pc, #0x2c4]
		MOV r1, #0
		BL       |sub_0804912C|
		MOV r0, #0
		LDR r4, [pc, #0x2bc]
		STR r0, [sp, #0x48]
		STR r0, [sp, #0x4c]
		LDR r1, [r4, #8]
		LDR r2, [r4]
		LDR r5, [pc, #0x290]
		SUB r1, r1, r2
		ASR r2, r1, #0x1f
		LSR r2, r2, #0x1d
		ADD r1, r2, r1
		ASR r2, r1, #3
		LDR r1, [r4, #0xc]
		LDR r3, [r4, #4]
		STR r2, [sp, #0x50]
		SUB r1, r1, r3
		ASR r3, r1, #0x1f
		LSR r3, r3, #0x1d
		ADD r1, r3, r1
		ASR r1, r1, #3
		STR r1, [sp, #0x54]
		LDR r1, [r5, #0x10]
		ADD r0, sp, #0x48
		LDRH r7, [r1]
		LDR r1, [pc, #0x28c]
		ADD r2, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x28c
		MOV r0, #3
		LSL r0, r0, #0x19
		LSL r1, r7, #6
		ADD r0, r1, r0
		STR r0, [sp, #0x58]
		LDR r1, [r4, #8]
		LDR r2, [r4]
		SUB r1, r1, r2
		LDR r2, [r4, #0xc]
		LDR r3, [r4, #4]
		SUB r2, r2, r3
		MUL r2, r1
		MOV r1, #0
		BL       |sub_0804912C|
		LDR r0, [r4, #8]
		LDR r1, [r4]
		SUB r1, r0, r1
		LDR r0, [r4, #0xc]
		LDR r2, [r4, #4]
		ADD r4, sp, #0x14
		SUB r2, r0, r2
		ADD r0, r4, #0
		BL       |loc_0803F540|
		LDR r0, [r5, #0x14]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		MOV r0, #0xe
		STRB r0, [r3, #0x15]
		MOV r0, #2
		STRB r0, [r3, #0x17]
		MOV r0, #1
		STRB r0, [r3, #0x16]
		LDR r0, [pc, #0x248]
		ADD r2, sp, #0x3c
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x3c]
		LDMIA r2!, {r1, r2}
		SUB r0, #8
		STR r0, [sp, #4]
		SUB r2, #8
		STR r2, [sp, #0x10]
		MOV r0, #0
		STR r0, [sp, #8]
		MOV r2, #0
		STR r1, [sp, #0xc]
		ADD r1, sp, #4
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x21f0
		LDR r0, [sp, #0x40]
		ADD r2, sp, #0x3c
		LDMIA r2!, {r1, r2}
		MOV r3, #0
		SUB r0, #8
		STR r2, [sp, #0x10]
		MOV r2, #0
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		ADD r1, sp, #4
		ADD r0, r4, #0
		STR r3, [sp, #4]
		BL       |inc_0x03d784_0x041118| + 0x21f0
		LDR r0, [sp, #0x3c]
		LDR r2, [sp, #0x40]
		SUB r0, #0xc
		SUB r2, #0xc
		STR r2, [sp, #0x10]
		MOV r1, #4
		SUB r2, #4
		SUB r3, r0, #4
		STR r2, [sp]
		STR r0, [sp, #0xc]
		ADD r0, sp, #0x14
		ADD r2, r1, #0
		STR r1, [sp, #4]
		STR r1, [sp, #8]
		BL       |loc_08004F1C|
		LDR r1, [sp, #0x40]
		LDR r0, [sp, #0x3c]
		MOV r2, #0
		SUB r1, #8
		SUB r0, #8
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		ADD r1, sp, #4
		ADD r0, r4, #0
		STR r2, [sp, #4]
		STR r2, [sp, #8]
		BL       |loc_08004F50|
		LDR r0, [sp, #0x68]
		MOV r4, #0x14
		STR r0, [sp, #8]
		B        |loc_08030D5A|
|loc_08030D56|
		CMP r1, #0
		BEQ      |loc_08030DBE|
|loc_08030D5A|
		LDR r1, [pc, #0x1c0]
		MOV r7, #8
		LDR r0, [r1, #8]
		LDR r1, [r1]
		SUB r0, r0, r1
		SUB r0, #0x18
		STR r0, [sp]
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #8
		BNE      |loc_08030D84|
|loc_08030D70|
		LDR r0, [sp, #8]
		ADD r3, sp, #0
		LDRH r0, [r0, #2]
		STRB r0, [r3, #0x17]
		LDR r0, [sp, #8]
		ADD r0, #4
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #8
		BEQ      |loc_08030D70|
|loc_08030D84|
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0x2d
		BNE      |loc_08030DBE|
		LDR r0, [sp, #8]
		ADD r0, #2
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0x20
		BNE      |loc_08030DA4|
|loc_08030D98|
		LDR r0, [sp, #8]
		ADD r0, #2
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0x20
		BEQ      |loc_08030D98|
|loc_08030DA4|
		LDR r0, [sp]
		LDR r2, [sp, #0x5c]
		SUB r0, #0x10
		STR r0, [sp]
		LDR r0, [r2]
		ADD r7, #0x10
		ADD r1, r0, #1
		LSL r0, r0, #3
		ADD r0, r0, r2
		ADD r0, #4
		STR r1, [r2]
		STR r4, [r0, #4]
		STR r7, [r0]
|loc_08030DBE|
		ADD r5, r7, #0
		ADD r3, sp, #4
		ADD r0, sp, #0x14
		LDR r1, [sp, #8]
		LDR r2, [sp]
		BL       |inc_0x03d784_0x041118| + 0x6e6
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		CMP r0, r1
		BEQ      |loc_08030E26|
|loc_08030DD4|
		LDR r0, [sp, #4]
		LDRH r0, [r0]
		CMP r0, #8
		BNE      |loc_08030DEC|
		LDR r0, [sp, #4]
		ADD r3, sp, #0
		LDRH r0, [r0, #2]
		STRB r0, [r3, #0x17]
		LDR r0, [sp, #4]
		ADD r0, #4
		STR r0, [sp, #4]
		B        |loc_08030E1E|
|loc_08030DEC|
		LDR r0, [sp, #4]
		STR r5, [sp, #0x18]
		STR r4, [sp, #0x1c]
		LDRH r1, [r0]
		ADD r0, sp, #0x14
		BL       |sub_0803DE50|
		LDR r0, [sp, #4]
		LDRH r0, [r0]
		LDR r1, [sp, #0x20]
		CMP r0, #0xff
		BLO      |loc_08030E0A|
		LDR r0, [r1, #4]
		ADD r0, #1
		B        |loc_08030E16|
|loc_08030E0A|
		LDR r1, [r1]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		ADD r0, #1
|loc_08030E16|
		ADD r5, r0, r5
		LDR r0, [sp, #4]
		ADD r0, #2
		STR r0, [sp, #4]
|loc_08030E1E|
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		CMP r0, r1
		BNE      |loc_08030DD4|
|loc_08030E26|
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0xa
		BEQ      |loc_08030E34|
		ADD r4, #0xe
		MOV r1, #0
		B        |loc_08030E44|
|loc_08030E34|
		MOV r1, #1
|loc_08030E36|
		LDR r0, [sp, #8]
		ADD r4, #0xe
		ADD r0, #2
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0xa
		BEQ      |loc_08030E36|
|loc_08030E44|
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0
		BNE      |loc_08030D56|
		LDR r0, [pc, #0xd4]
		LDR r0, [r0]
		CMP r0, #0
		BEQ      |loc_08030E7E|
		MOV r0, #2
		ADD r3, sp, #0
		STRB r0, [r3, #0x14]
		LDR r0, [sp, #0x3c]
		LDR r1, [sp, #0x40]
		SUB r0, #0x10
		STR r0, [sp, #0x18]
		SUB r1, #0x10
		STR r1, [sp, #0x1c]
		LDR r0, [pc, #0x90]
		LDR r1, [pc, #0xbc]
		LDR r0, [r0, #8]
		ADD r0, r0, r1
		LDR r2, [r0]
		MOV r0, #0x99
		LDR r1, [pc, #0xb8]
		LSL r0, r0, #2
		LDR r1, [r1, r0]
		ADD r0, sp, #0x14
		BL       |sub_0803DC96|
|loc_08030E7E|
		LDR r0, [r6, #0x10]
		CMP r0, #0
		BEQ      |loc_08030EA4|
		MOV r0, #0
		LDR r1, [pc, #0x7c]
		CMP r6, #0
		STR r0, [r1]
		BEQ      |loc_08030E90|
		LDR r0, [sp, #0x60]
|loc_08030E90|
		ADD r1, r0, #0
		MOV r0, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x24d6
		ADD r1, r0, #0
		STR r0, [r6, #0x54]
		LDR r0, [pc, #0x58]
		LDR r0, [r0, #4]
		BL       |List_Append|
|loc_08030EA4|
		LDR r4, [pc, #0x74]
		LDR r0, [r4, #8]
		LDR r1, [r4]
		SUB r0, r0, r1
		LDR r1, [r4, #0xc]
		LDR r2, [r4, #4]
		SUB r1, r1, r2
		MUL r0, r1
		LDR r1, [sp, #0x38]
		ADD r3, r0, #0
		ADD r0, r1, #0
		LDR r2, [pc, #0x74]
		BL       |sub_0804918C|
		LDR r0, [r4]
		LDR r1, [r4, #4]
		LDR r2, [pc, #0x6c]
		NEG r0, r0
		STRH r0, [r2]
		NEG r1, r1
		STRH r1, [r2, #2]
		ADD r1, r2, #0
		ADD r1, #0x30
		LDRH r0, [r1, #0x10]
		LSL r0, r0, #0x1a
		BNE      |loc_08030F48|
		LDR r0, [pc, #0x5c]
		MOV r3, #0
		STR r0, [r6, #0x60]
		MOV r0, #1
		STR r0, [r6, #0x5c]
		LDR r0, [pc, #0x58]
		LDR r2, [pc, #0x58]
		STRB r3, [r0]
		MOV r0, #0x10
		STRB r0, [r2]
		LDR r0, [pc, #0x54]
		STR r3, [r6, #0x58]
		STRH r0, [r1, #0x10]
		B        |loc_08030F50|
	INCBIN  baserom.gba_0x30ef4_0x30ef8.extracted
		DCD     0x08759154
	INCBIN  baserom.gba_0x30efc_0x30f04.extracted
		DCD     0x03002A60
	INCBIN  baserom.gba_0x30f08_0x30f0c.extracted
		DCD     0x0804E454
		DCD     0x080496B4
		DCD     0x0804ABD8
		DCD     VRAM + 0xE000
		DCD     0x03000F50
		DCD     0x0803F5A5
		DCD     0x03000F4C
		DCD     0x000004F4
		DCD     0x0806BCE8
		DCD     0x0805672C
		DCD     REG_BG0HOFS
		DCD     0x08030BF5
		DCD     REG_BLDALPHA
		DCD     0x04000053
		DCD     0x00003E41
|loc_08030F48|
		LDR r0, [pc, #0x9c]
		STR r0, [r6, #0x60]
		MOV r0, #0
		STR r0, [r6, #0x5c]
|loc_08030F50|
		MOV r0, #0x39
		LSL r0, r0, #7
		MOV r1, #1
		LSL r1, r1, #0x1a
		STRH r0, [r1, #8]
		LDR r1, [sp, #0x58]
		ADD r0, sp, #0x14
		BL       |sub_08049150|
		LDR r0, [pc, #0x88]
		MOV r1, #0
		LDR r0, [r0, #0xc]
		BL       |loc_080096AC|
		MOV r1, #0
		ADD r0, sp, #0x14
		BL       |sub_0803F58C|
		ADD r0, r6, #0
		B        |inc_0x301c0_0x311c0| + 0xa6a
