	CODE16
|loc_080258A4|
		MOV r7, lr
		LDR r0, [r7]
		LSL r0, r0, #3
		STR r0, [r7]
		LDR r0, [r7, #4]
		LSL r0, r0, #3
		STR r0, [r7, #4]
		LDR r0, [pc, #0x23c]
		ADD r0, r4, r0
		LDR r1, [r0]
		LSL r1, r1, #3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LSL r1, r1, #3
		STR r1, [r0, #4]
		MOV r0, #1
		LSL r0, r0, #0xf
		ADD r5, r4, r0
		LDR r0, [r5, #0x1c]
		ADD r1, r0, #0
		SUB r1, #0xdf
		STR r1, [r5, #0xc]
		LDR r1, [r5, #0x20]
		SUB r0, #0x10
		ADD r2, r1, #0
		SUB r2, #0x8f
		STR r2, [r5, #0x10]
		LDR r2, [r5, #0x24]
		SUB r1, #0x10
		ADD r3, r2, #0
		SUB r3, #0x11
		STR r3, [r5, #0x14]
		LDR r3, [r5, #0x28]
		ADD r5, #0x1c
		ADD r6, r3, #0
		SUB r3, #0x90
		SUB r2, #0xe0
		STMIA r5!, {r0, r1, r2, r3}
		SUB r5, #0x2c
		LDR r0, [pc, #0x1ec]
		SUB r6, #0x11
		STR r6, [r5, #0x18]
		LDR r0, [r0, #0xc]
		MOV r1, #0x2f
		ADD r6, r0, #0
		LDR r0, [pc, #0x1e0]
		ADD r6, #0x94
		LDR r0, [r0, #4]
		LSL r1, r1, #6
		ADD r0, r0, r1
		MOV r2, #0
		MOV r1, #9
		LDR r0, [r0, #0x38]
		BL       |loc_08011C70|
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #0xd4]
		ADD r0, r1, #0
		STR r1, [sp, #0xd0]
		LDR r1, [sp, #0xd4]
		LDR r7, [sp, #0xe0]
		STR r0, [sp, #0xd8]
		STR r1, [sp, #0xdc]
		ADD r7, #4
		LDR r0, [r7, #8]
		LDR r1, [r7]
		SUB r0, r0, r1
		LSL r1, r0, #3
		LDR r0, [sp, #0xd8]
		MUL r1, r0
		LDR r0, [r6]
		ASR r2, r0, #1
		ADD r1, r1, r2
		BL       |sub_08046E58|
		LDR r1, [sp, #0xe0]
		LDR r1, [r1, #4]
		LSL r1, r1, #3
		ADD r0, r0, r1
		STR r0, [r5, #0x2c]
		LDR r0, [r7, #0xc]
		LDR r1, [r7, #4]
		SUB r0, r0, r1
		LSL r1, r0, #3
		LDR r0, [sp, #0xdc]
		MUL r1, r0
		LDR r0, [r6, #4]
		ASR r2, r0, #1
		ADD r1, r1, r2
		BL       |sub_08046E58|
		LDR r1, [sp, #0xe0]
		LDR r1, [r1, #8]
		LSL r1, r1, #3
		ADD r0, r0, r1
		STR r0, [r5, #0x30]
		LDR r0, [pc, #0x16c]
		ADD r2, r4, r0
		ADD r6, r2, #0
		ADD r1, r4, #0
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0xaaf4
		ADD r1, r0, #0
		LDR r0, [pc, #0x160]
		LDR r0, [r0, #4]
		BL       |List_Append|
		LDR r0, [r5, #0x2c]
		SUB r0, #0x78
		STR r0, [r5, #0x2c]
		LDR r0, [r5, #0x30]
		SUB r0, #0x50
		STR r0, [r5, #0x30]
		LDR r0, [r6]
		ADD r0, #0xf0
		STR r0, [r6, #8]
		LDR r0, [r6, #4]
		ADD r0, #0xa0
		STR r0, [r6, #0xc]
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r0, [r0, #4]
		DCW     0xF017
		DCW     0xFE07
		ADD r5, r0, #0
		LDR r0, [sp, #0xe8]
		ADD r1, r5, #0
		LDR r0, [r0]
		LDR r0, [r0]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r0, [sp, #0xe8]
		ADD r1, r5, #0
		LDR r0, [r0]
		LDR r0, [r0]
		LDR r2, [r0, #4]
		MOV r0, #3
		LSL r0, r0, #0x19
		BL       |Thunk_VramCopy|
		ADD r0, r5, #0
		DCD     0xFE36F017
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r1, [r0, #8]
		CMP r1, #0
		BEQ      |loc_08025A82|
		LDR r0, [r0, #0x10]
		LDR r7, [pc, #0x100]
		LDR r1, [r0, #4]
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
		ADD r6, r0, #0
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r0, [r0, #0x10]
		LDR r0, [r0, #4]
		DCD     0xFDE2F017
		ADD r5, r0, #0
		LDR r0, [sp, #0xe8]
		ADD r1, r5, #0
		LDR r0, [r0]
		LDR r0, [r0, #0x10]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r1, [pc, #0xf0]
		LSL r0, r6, #5
		ADD r0, r0, r1
		LDR r1, [sp, #0xe8]
		LDR r1, [r1]
		LDR r1, [r1, #0x10]
		LDR r2, [r1, #4]
		ADD r1, r5, #0
		BL       |Thunk_VramCopy|
		ADD r0, r5, #0
		DCD     0xFE10F017
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r7, [r0, #0xc]
		MOV r0, #0x20
		DCD     0xFDC8F017
		ADD r5, r0, #0
		BEQ      |loc_08025A3E|
		MOV r3, #0
		ADD r2, r7, #0
		ADD r1, r4, #0
		ADD r0, r5, #0
		STR r6, [sp]
		BL       |inc_0x1c3f2_0x2ab4c| + 0xa8aa
		LDR r0, [pc, #0xbc]
		STR r0, [r5]
|loc_08025A3E|
		LDR r7, [pc, #0xa0]
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |List_Append|
		LDR r0, [sp, #0xe8]
		MOV r5, #1
		LDR r0, [r0]
		LDR r0, [r0, #8]
		CMP r0, #1
		BLE      |loc_08025A82|
|loc_08025A54|
		LDR r0, [sp, #0xe8]
		STR r6, [sp]
		LDR r0, [r0]
		LSL r1, r5, #1
		ADD r1, r1, r5
		LDR r0, [r0, #0xc]
		LSL r1, r1, #3
		ADD r2, r0, r1
		ADD r3, r5, #0
		ADD r1, r4, #0
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0xa8aa
		ADD r1, r0, #0
		LDR r0, [r7, #4]
		BL       |List_Append|
		LDR r0, [sp, #0xe8]
		ADD r5, #1
		LDR r0, [r0]
		LDR r0, [r0, #8]
		CMP r0, r5
		BGT      |loc_08025A54|
|loc_08025A82|
		LDR r0, [sp, #0xe8]
		LDR r0, [r0]
		LDR r1, [r0, #4]
		CMP r1, #0
		BEQ      |loc_08025A9A|
		MOV r3, #0
		STR r3, [sp]
		STR r3, [sp, #0x44]
		MOV r2, #0
		MOV r0, sp
		BL       |loc_08004038|
|loc_08025A9A|
		MOV r2, #0
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08026B4C|
		LDR r5, [pc, #0x38]
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |List_Append|
		MOV r2, #1
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08026B4C|
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |List_Append|
		MOV r2, #2
		ADD r1, r4, #0
		MOV r0, #0
		BL       |loc_08026B4C|
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |List_Append|
		DCW     0xE013
	INCBIN  baserom.gba_0x25ad4_0x25adc.extracted
		DCD     0x0000802C
		DCD     0x08732360
	INCBIN  baserom.gba_0x25ae4_0x25af0.extracted
		DCD     0x00008024
		DCD     VRAM + 0x10000
	INCBIN  baserom.gba_0x25af8_0x25afa.extracted
