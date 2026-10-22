	CODE16
|sub_080273AA|
|unk_080273AA|
		LDR r0, [r5]
		LDR r1, [pc, #0xc4]
		LSL r0, r0, #4
		ADD r0, r0, r1
		LDR r0, [r0, #4]
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		LDR r2, [pc, #0xb8]
		BL       |loc_0800EB60|
		LDR r0, [pc, #0xb8]
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0x81
		STR r5, [r0, #0xc]
		LDR r1, [r5, #8]
		LSL r1, r1, #0x18
		LSR r1, r1, #0x18
		STRB r1, [r4, #0x10]
		LDRB r3, [r4, #0x11]
		LDR r2, [r4, #0x50]
		LSL r1, r1, #2
		LSL r3, r3, #4
		ADD r2, r2, r3
		ADD r1, r2, r1
		LDR r1, [r1, #4]
		STR r1, [r4, #0x54]
		LDR r2, [r5, #0xc]
		LDR r3, [r5, #0x10]
		STR r2, [r4, #0x6c]
		STR r3, [r4, #0x70]
		MOV r3, #4
		LDRSB r7, [r1, r3]
		MOV r3, #5
		LDRSB r1, [r1, r3]
		LDR r6, [r5, #0xc]
		ADD r2, r5, #0
		LDR r5, [r5, #0x10]
		ADD r2, #0x14
		ADD r1, r5, r1
		STR r1, [r2, #4]
		ADD r6, r6, r7
		STR r6, [r2]
		LDR r1, [r0, #0xc]
		LDR r3, [r4, #0x54]
		ADD r1, #0x14
		LDRB r2, [r3, #6]
		LDR r5, [r1]
		LDRB r3, [r3, #7]
		ADD r2, r5, r2
		STR r2, [r1, #8]
		LDR r2, [r1, #4]
		ADD r2, r2, r3
		STR r2, [r1, #0xc]
		LDR r0, [r0, #0xc]
		STR r4, [r0, #0x24]
		ADD r0, r4, #0
		DCW     0xE7C1
