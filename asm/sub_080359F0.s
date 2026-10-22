	CODE16
|sub_080359F0|
|unk_080359F0|
		MOV r1, #1
		LSL r1, r1, #0xb
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x180]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r6, #1
		ADD r0, r0, r6
		LDR r1, [pc, #0x174]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		LDR r2, [pc, #0x16c]
		LSL r0, r6, #3
		LDR r1, [r2, r0]
		ADD r0, r0, r2
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x82e
