	CODE16
|sub_0803046E|
|unk_0803046E|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #0xa1
		LDR r0, [r5, #4]
		LDR r1, [r5]
		STR r0, [sp, #0x28]
		STR r1, [sp, #0x24]
		LDR r1, [sp, #0x28]
		MOV r0, #1
		LSL r0, r0, #0xe
		ADD r0, r1, r0
		STR r0, [sp, #0x28]
		MOV r0, #0x2d
		ADD r7, sp, #0x24
		BL       |inc_0x0158_0x143f2|
		ADD r2, r0, #0
		ADD r2, #8
		ADD r1, r7, #0
		LDR r0, [r6, #4]
		BL       |loc_08009904|
		CMP r0, #0
		BNE      |loc_080304A2|
		MOV r0, #1
		B        |inc_0x301c0_0x311c0| + 0x2aa
|loc_080304A2|
		LDR r1, [pc, #0x38]
		MOV r2, #0x20
		ADD r7, sp, #4
		ADD r1, #8
		ADD r0, r7, #0
		BL       |Thunk_VramCopy|
		LDR r0, [r5]
		ADD r3, sp, #0
		ASR r0, r0, #8
		STRH r0, [r3, #0x10]
		MOV r0, #0xff
		ADD r0, #0xa5
		LDR r0, [r0, r4]
		LDR r2, [pc, #0x20]
		ASR r0, r0, #8
		STRH r0, [r3, #0x12]
		MOV r3, #0
		MVN r3, r3
		ADD r1, r7, #0
		MOV r0, #0
		BL       |loc_0800F68C|
		ADD r1, r0, #0
		LDR r0, [r6]
		BL       |List_Append|
		MOV r0, #1
		B        |inc_0x301c0_0x311c0| + 0x2aa
	INCBIN  baserom.gba_0x304dc_0x304de.extracted
