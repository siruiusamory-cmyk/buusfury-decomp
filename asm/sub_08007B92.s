	CODE16
|sub_08007B92|
|unk_08007B92|
		LDR r0, [pc, #0x2d4]
		STRB r6, [r4, #4]
		STR r0, [r4]
		ADD r3, r4, #0
		ADD r3, #0x20
		STR r5, [r4, #8]
		MOV r7, #0xff
		STRB r7, [r3]
		STRB r7, [r3, #1]
		STRB r7, [r3, #2]
		STRB r7, [r3, #3]
		LDR r3, [pc, #0x2c0]
		ADD r0, r4, #0
		STR r3, [r4, #0x10]
		STR r3, [r4, #0x14]
		STR r3, [r4, #0x18]
		STR r3, [r4, #0x1c]
		MOV r3, #0x16
		LDRSH r7, [r5, r3]
		ADD r3, r5, #4
		ADD r0, #0x3c
		STR r7, [r4, #0xc]
		LDR r5, [r5, #4]
		ADD r2, r0, #4
		STR r5, [r0]
		LDR r0, [r3, #4]
		ADD r1, r2, #4
		STR r0, [r2]
		LDR r0, [r4, #8]
		ADD r6, r1, #4
		ADD r0, #0xc
		LDMIA r0!, {r2}
		STR r2, [r1]
		LDR r0, [r0]
		STR r0, [r6]
		LDR r0, [r4, #8]
		ADD r0, #0x14
		LDRB r6, [r0]
		LDRB r0, [r0, #1]
		MUL r6, r0
		CMP r6, #4
		BGT      |loc_08007C0E|
		MOV r5, #0
		CMP r6, #0
		BLE      |loc_08007C0E|
|loc_08007BEC|
		LDR r0, [r4, #8]
		LSL r1, r5, #2
		ADD r0, r0, r1
		LDR r0, [r0, #0x18]
		CMP r0, #0
		BEQ      |loc_08007C08|
		ADD r1, r4, r5
		ADD r1, #0x20
		STRB r5, [r1]
		LSL r1, r5, #0xb
		ADD r1, r1, r4
		ADD r1, #0x4c
		BL       |inc_0x03d784_0x041118| + 0x1bc
|loc_08007C08|
		ADD r5, #1
		CMP r5, r6
		BLT      |loc_08007BEC|
|loc_08007C0E|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x7a38
