	CODE16
|sub_08038CDC|
|unk_08038CDC|
		ASR r1, r1, #3
		LSL r3, r1, #1
		ADD r1, r3, r1
		LDR r0, [r4, #0x5c]
		LSL r1, r1, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		B        |loc_08038D5E|
|loc_08038CEC|
|unk_08038CEC|
; cited by 0x08038B0A (a pc-relative load targets 0x08038DC8)
		LDR r2, [r4, #0x58]
		LDRH r2, [r2, #2]
		LSL r3, r2, #0x1a
		LSR r3, r3, #0x1f
		BEQ      |loc_08038D0C|
		MOV r3, #0x37
		LDR r2, [r4, #0x50]
		MVN r3, r3
		CMP r2, r3
		BLE      |loc_08038D22|
		SUB r2, #3
		STR r2, [r4, #0x50]
		LDR r2, [r4, #0x20]
		SUB r2, r2, r1
		STR r2, [r0]
		B        |loc_08038D22|
|loc_08038D0C|
		LSL r2, r2, #0x1b
		LSR r2, r2, #0x1f
		BEQ      |loc_08038D22|
		LDR r2, [r4, #0x50]
		CMP r2, #0x38
		BGE      |loc_08038D22|
		ADD r2, #3
		STR r2, [r4, #0x50]
		LDR r2, [r4, #0x20]
		ADD r2, r2, r1
		STR r2, [r0]
|loc_08038D22|
		LDR r0, [r4, #0x58]
		LDRH r2, [r0, #2]
		LSL r0, r2, #0x19
		LSR r3, r0, #0x1f
		ADD r0, r4, #0
		ADD r0, #0x24
		CMP r3, #0
		BEQ      |loc_08038D48|
		MOV r3, #0x1f
		LDR r2, [r4, #0x54]
		MVN r3, r3
		CMP r2, r3
		BLE      |loc_08038D5E|
		SUB r2, #3
		STR r2, [r4, #0x54]
		LDR r2, [r4, #0x24]
		SUB r1, r2, r1
		STR r1, [r0]
		B        |loc_08038D5E|
|loc_08038D48|
		LSL r2, r2, #0x18
		LSR r2, r2, #0x1f
		BEQ      |loc_08038D5E|
		LDR r2, [r4, #0x54]
		CMP r2, #0x20
		BGE      |loc_08038D5E|
		ADD r2, #3
		STR r2, [r4, #0x54]
		LDR r2, [r4, #0x24]
		ADD r1, r2, r1
		STR r1, [r0]
|loc_08038D5E|
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |loc_08038DA6|
		CMP r6, #0
		BEQ      |loc_08038DA6|
		LDRB r0, [r5]
		CMP r0, #0
		BNE      |loc_08038DA6|
		LDR r1, [r4, #0x1c]
		ADD r3, sp, #0
		STR r1, [sp, #0x20]
		LDRB r1, [r4, #0x10]
		ADD r5, r4, #0
		ADD r5, #0x28
		STRB r1, [r3, #0x14]
		LDR r1, [pc, #0x60]
		MOV r0, sp
		STR r1, [sp, #0x1c]
		MOV r1, #0xff
		ADD r1, #0x49
		STR r1, [sp, #0x18]
		MOV r1, #1
		STRB r1, [r3]
		STR r4, [sp, #0x30]
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r6, r0, #4
		STMIA r6!, {r1, r2, r3, r5}
		ADD r2, r0, #0
		LDR r0, [pc, #0x34]
		MOV r1, #0
		LDR r0, [r0]
		BL       |loc_08011C0C|
|loc_08038DA6|
		LDR r0, [r4, #0x14]
		LDR r1, [r4, #0x18]
		CMP r0, r1
		BEQ      |inc_0x351c0_0x3d4d0| + 0x3b18
		STR r1, [r4, #0x14]
		LDRB r2, [r1, #2]
		LDRB r0, [r1, #3]
		LDR r3, [pc, #0x30]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		B        |inc_0x351c0_0x3d4d0| + 0x3b18
	DCB	0x00,0x00
	DCD	0x0804D1B8
	DCD	|unk_0877AD10|
	DCD	0x0807268C
		DCD     0x0877110C
	INCBIN  baserom.gba_0x38dd8_0x38de2.extracted
|sub_08038DE2|
	DCW      0x0804
	DCW      0x8118
	DCW      0x086b
	DCW      0x0000
	DCW      0x0601
