	CODE16
|sub_0802C0B0|
|unk_0802C0B0|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |inc_0x2bb4c_0x2d1c0| + 0x560
		LDR r5, [pc, #0xd8]
		LDR r0, [r5, #4]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |inc_0x2bb4c_0x2d1c0| + 0x560
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xb0]
		ADD r1, #8
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		ADD r3, r4, #0
		MOV r0, #0
		LDRB r2, [r4, #0x10]
		ADD r1, sp, #0x14
		BL       |inc_0x2bb4c_0x2d1c0| + 0xc44
		ADD r1, r0, #0
		LDR r0, [r5, #4]
		BL       |List_Append|
		MOV r1, #0xb7
		LDR r2, [pc, #0x7c]
		LSL r1, r1, #2
		ADD r1, r1, r2
		LDR r4, [pc, #0x7c]
		LDR r0, [r5]
		MOV r2, #0x40
		MOV r3, #0
		ADD r0, r0, r4
		BL       |inc_0x03d784_0x041118| + 0xbf4
		B        |inc_0x2bb4c_0x2d1c0| + 0x560
