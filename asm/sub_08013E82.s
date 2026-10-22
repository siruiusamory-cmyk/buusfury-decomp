	CODE16
|sub_08013E82|
|unk_08013E82|
		LDR r0, [sp, #8]
		LDR r1, [pc, #0x28c]
		STR r0, [r4, #4]
		LDR r0, [pc, #0x284]
		STR r0, [r4]
		STR r6, [r4, #8]
		STR r7, [r4, #0xc]
		MOV r0, #1
		STR r0, [r4, #0x10]
		STR r5, [r4, #0x14]
		LDR r0, [sp, #0xc]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x20]
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x24]
		LDR r2, [sp, #0x28]
		STR r2, [r4, #0x28]
		LDRB r3, [r0, #4]
		LDRB r5, [r0, #5]
		ADD r0, #4
		ADD r1, r1, r3
		STR r1, [r4, #0x2c]
		ADD r1, r2, r5
		STR r1, [r4, #0x30]
		LDRB r1, [r0]
		LDRB r0, [r0, #1]
		MUL r1, r0
		LSL r0, r1, #1
		ADD r0, r0, r1
		STR r1, [r4, #0x34]
		DCD     0xFB78F029
		MOV r5, #0
		STR r0, [r4, #0x38]
|loc_08013ECC|
		LDR r0, [r4, #0x20]
		LDR r2, [r4, #0x38]
		LDR r1, [r0, #8]
		LDR r0, [r4, #0x34]
		MUL r0, r5
		ADD r0, r2, r0
		LSL r2, r5, #2
		ADD r1, r2, r1
		LDR r1, [r1, #4]
		BL       |inc_0x049120_0x055620|
		ADD r5, #1
		CMP r5, #3
		BLT      |loc_08013ECC|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x13d26
