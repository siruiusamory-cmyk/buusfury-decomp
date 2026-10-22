	CODE16
|loc_08005BFE|
		STR r2, [sp, #4]
		LDRB r2, [r7, #1]
		LDRB r1, [r7]
		LDR r0, [r6, #0x18]
		BL       |loc_08008D44|
		LDR r0, [r6, #0x10]
		MOV r3, #0x68
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0x14]
		LDR r1, [pc, #0x1c4]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
		MOV r0, #0xc
		DCD     0xFCC4F037
		CMP r0, #0
		DCW     0xD004
		LDR r1, [pc, #0x1b0]
		STMIA r0!, {r1, r5}
		SUB r0, #8
		MOV r1, #4
		STR r1, [r0, #8]
	INCBIN  baserom.gba_0x5c3e_0x5c40.extracted
|sub_08005C40|
|unk_08005C40|
	INCBIN	baserom.gba_0x5c40_0x5c44.extracted
	BL       |loc_080042FC|
	LDR      r0, [r6, #0x10]
	BL       |Object_SubtractDelta1|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08005C5C|
	LDR      r1, [pc, #0x180]
	STR      r1, [r0]
|loc_08005C5C|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r1, #0
	LDR      r0, [pc, #0x188]
	BL       |sub_08012588|
	MOV      r0, #1
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_08005C6E|
|unk_08005C6E|
; cited by 0x080059D2 (a pc-relative load targets 0x08005DA4)
	INCBIN  baserom.gba_0x5c6e_0x5e36.extracted
|loc_08005E36|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x5b12
