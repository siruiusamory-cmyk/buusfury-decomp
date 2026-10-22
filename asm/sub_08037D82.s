	CODE16
|sub_08037D82|
|unk_08037D82|
		CMP r0, #0x1c
		BHS      |loc_08037D8C|
		MOV r0, #2
		STRB r0, [r4, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0x2bbe
|loc_08037D8C|
		LDR r6, [pc, #0x104]
		LDR r5, [pc, #0x108]
		CMP r0, #0x20
		BHS      |loc_08037DFE|
		MOV r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #0x1c
		BNE      |inc_0x351c0_0x3d4d0| + 0x2bbe
		LDR r0, [r5]
		BL       |loc_080116FC|
		MOV r1, #7
		LSL r1, r1, #8
		CMP r0, r1
		BLT      |inc_0x351c0_0x3d4d0| + 0x2bbe
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [sp, #4]
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		LDRB r0, [r4, #0x10]
		ADD r1, r5, #4
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #8]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0xc]
		LDR r0, [r0, #4]
		STR r1, [sp]
		ADD r0, r2, r0
		STR r0, [sp, #4]
		ADD r0, r1, #0
		LDR r1, [sp, #4]
		STR r0, [sp, #0x10]
		STR r1, [sp, #0x14]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x10
		BL       |inc_0x351c0_0x3d4d0| + 0x2ce8
		ADD r1, r0, #0
		STR r0, [r6, #4]
		LDR r0, [r5]
		BL       |List_Append|
		B        |inc_0x351c0_0x3d4d0| + 0x2bbe
|loc_08037DFE|
		LDR r0, [r5]
		LDR r3, [r6, #4]
		ADD r1, r0, #4
		LDR r5, [r1]
		MOV r0, #0
		CMP r5, #0
		BLE      |loc_08037E1C|
|loc_08037E0C|
		LSL r2, r0, #2
		ADD r2, r2, r1
		LDR r2, [r2, #4]
		CMP r2, r3
		BEQ      |inc_0x351c0_0x3d4d0| + 0x2bbe
		ADD r0, #1
		CMP r5, r0
		BGT      |loc_08037E0C|
|loc_08037E1C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
	INCBIN  baserom.gba_0x37e26_0x37e28.extracted
|sub_08037E28|
|unk_08037E28|
	INCBIN	baserom.gba_0x37e28_0x37e2c.extracted
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x6c]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x64]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_08037E4A|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08037E4A|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x38]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x40]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_08037E76|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08037E76|
	ADD      sp, #0x10
	POP      {r4, pc}
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0x14]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08037E88|
	MOV      r0, #0
|loc_08037E88|
	SUB      r0, r2, r0
	BX       lr
	LDR      r0, [pc, #4]
	ADD      r0, #8
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0x94
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r4, r5, r7}
	LSR      r6, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_08037EC4|
	MOV      r0, #0x5c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08037EC4|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
