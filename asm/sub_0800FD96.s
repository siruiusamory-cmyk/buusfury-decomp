	CODE16
|sub_0800FD96|
|unk_0800FD96|
		ADD r2, r7, #0
		ADD r0, r4, #0
		LDR r1, [sp, #8]
		BL       |inc_0x0158_0x143f2| + 0xf434
		LDR r0, [pc, #0x264]
		MOV r7, #0xff
		ADD r7, #0xa9
		MOV r3, #0xf
		LSL r3, r3, #0xc
		STR r0, [r4]
		STR r3, [r7, r4]
		MOV r3, #0
		ADD r2, r7, #4
		STR r3, [r2, r4]
		MOV r2, #0xff
		ADD r2, #0x99
		STR r6, [r2, r4]
		LDR r3, [r4, #0x58]
		ADD r2, #4
		LDRH r3, [r3, #8]
		ADD r1, r4, #0
		ADD r1, #0xff
		STRH r3, [r2, r4]
		MOV r3, #0
		LDRSH r2, [r5, r3]
		MOV r3, #2
		LDRSH r5, [r5, r3]
		ADD r1, #0xa1
		LSL r2, r2, #8
		STR r2, [r1]
		ADD r0, r1, #4
		LSL r3, r5, #8
		STR r3, [r0]
		LDR r0, [r4, #0x58]
		LDRB r2, [r0, #0xa]
		LDRB r1, [r0, #0xc]
		LSR r2, r2, #1
		ADD r2, r1, r2
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0x91
		STRB r2, [r1, #0xe]
		LDRB r2, [r0, #0xd]
		LDRB r0, [r0, #0xb]
		LSR r0, r0, #1
		ADD r0, r2, r0
		STRB r0, [r1, #0xf]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xfc3a
