	CODE16
|sub_0800E776|
|unk_0800E776|
		STR r7, [sp]
		ADD r2, sp, #8
		ADD r3, r6, #0
		ADD r0, r4, #0
		LDMIA r2!, {r1, r2}
		BL       |inc_0x0158_0x143f2| + 0xfc1c
		LDR r0, [pc, #0x3ac]
		ADD r1, r4, #0
		ADD r1, #0xff
		STR r0, [r4]
		ADD r1, #0xc1
		MOV r2, #0
		STR r2, [r1, #0x10]
		STR r2, [r1, #0x14]
		STR r2, [r1, #0x18]
		STR r2, [r1, #0x1c]
		STR r2, [r1, #0x20]
		MOV r0, #1
		STR r0, [r1, #0xc]
		STR r2, [r1, #8]
		LDRB r6, [r5, #0xd]
		ADD r0, r1, #0
		SUB r0, #0x20
		STRH r6, [r0, #0x10]
		LDRB r6, [r5, #0xe]
		ADD r3, r1, #4
		STRH r6, [r0, #0x12]
		LDRB r6, [r5, #0xf]
		STRH r6, [r0, #0x14]
		LDRB r6, [r5, #0xf]
		STRH r6, [r0, #0x16]
		LDRB r6, [r5, #0x10]
		ADD r0, #0x10
		STRB r6, [r0, #8]
		LDRB r5, [r5, #0x11]
		STRB r5, [r0, #9]
		MOV r0, #0xff
		ADD r0, #0xbd
		STR r2, [r0, r4]
		MOV r0, #1
		LSL r0, r0, #0xc
		STR r0, [r1]
		STR r2, [r3]
		LDR r0, [pc, #0x368]
		STR r2, [r1, #0x24]
		LDR r0, [r0, #4]
		STR r0, [r1, #0x28]
		STR r0, [r1, #0x2c]
		MOV r0, #1
		LSL r0, r0, #9
		ADD r0, r4, r0
		STR r2, [r0, #4]
		STR r2, [r1, #0x34]
		STR r2, [r1, #0x30]
		STR r2, [r1, #0x38]
		STR r2, [r1, #0x3c]
		STR r2, [r0, #0x10]
		STR r2, [r0, #0x14]
		STR r2, [r0, #0x18]
		STR r2, [r0, #0x1c]
		STR r2, [r0, #0x20]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xe61a
