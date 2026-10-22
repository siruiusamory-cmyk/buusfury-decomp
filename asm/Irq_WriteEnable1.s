|Irq_WriteEnable1|
	CODE16
|unk_080080D8|
		LDR r0, [pc, #0x3b8]
		MOV r2, #4
		STR r0, [r4]
		LSL r0, r2, #7
		LDR r7, [pc, #0x3b4]
		ADD r1, r4, r0
		ADD r5, r4, #0
		ADD r5, #0x5c
		ADD r6, r1, #0
		ADD r3, r7, #0
		ADD r0, r5, #4
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r3, r7, #0
		MOV r7, #0x1d
		LSL r7, r7, #5
		ADD r1, r4, r7
		MOV r2, #4
		ADD r0, r6, #0
		BL       |__vecmap1c__FPvT1iPFPv_v|
		LDR r0, [sp, #8]
		LDR r3, [pc, #0x380]
		STR r0, [r4, #4]
		MOV r0, #0
		ADD r3, #8
		MOV r2, #0xff
		STR r0, [r5]
|loc_08008110|
		LSL r1, r0, #2
		ADD r1, r1, r4
		STR r2, [r1, #0x2c]
		ADD r0, #1
		CMP r0, #9
		STR r3, [r1, #8]
		BLT      |loc_08008110|
		LDR r0, [r4, #4]
		ADD r0, #4
		LDRB r6, [r0]
		LDRB r0, [r0, #1]
		MUL r6, r0
		CMP r6, #9
		BGT      |loc_08008152|
		MOV r5, #0
		CMP r6, #0
		BLE      |loc_08008152|
|loc_08008132|
		LDR r0, [r4, #4]
		LSL r1, r5, #2
		ADD r0, r0, r1
		LDR r0, [r0, #8]
		CMP r0, #0
		BEQ      |loc_0800814C|
		ADD r1, r1, r4
		STR r5, [r1, #0x2c]
		LSL r1, r5, #0xa
		ADD r1, r1, r4
		ADD r1, r1, r7
		BL       |inc_0x03d784_0x041118| + 0x1bc
|loc_0800814C|
		ADD r5, #1
		CMP r5, r6
		BLT      |loc_08008132|
|loc_08008152|
		LDR r0, [pc, #0x334]
		LDR r1, [pc, #0x344]
		LDR r0, [r0]
		LDR r2, [pc, #0x344]
		STR r1, [r0, #4]
		LDRH r0, [r2]
		MOV r1, #2
		ORR r0, r1
		ADD r1, r2, #0
		SUB r1, #0xff
		STRH r0, [r2]
		MOV r0, #0
		SUB r1, #0xe1
		STRH r0, [r1, #2]
		STRH r0, [r1, #6]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x7f7c
