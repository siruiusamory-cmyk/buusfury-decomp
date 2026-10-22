	CODE16
|sub_0803A4C6|
|unk_0803A4C6|
		SUB r1, #1
		STRH r1, [r0, #0x12]
		LSR r1, r1, #3
		STRB r1, [r0, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0x5304
		PUSH {r3, r4, r5, lr}
		ADD r4, r1, #0
		LDR r1, [r0, #4]
		MOV r5, #1
		CMP r1, #0
		BNE      |loc_0803A4EE|
		MOV r1, #0x12
		STR r5, [r0, #4]
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		LDR r1, [pc, #0x3c]
		ADD r0, r4, #0
		BL       |loc_0800ED18|
|loc_0803A4EE|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		LDR r1, [r0]
		ADD r1, #0x80
		STR r1, [r0]
		LDR r0, [r4, #0x58]
		ADD r0, #0x48
		LDR r0, [r0, #0x54]
		LDR r1, [r4, #0x50]
		CMP r0, r1
		BNE      |sub_0803A50A|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x534c
