	CODE16
|sub_08004D56|
|unk_08004D56|
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0x81
		MOV r2, #0x80
		ADD r0, r4, #0
		LDR r3, [pc, #0x9c]
		BL       |__vecmap1c__FPvT1iPFPv_v|
		LDR r7, [pc, #0x84]
		ADD r6, sp, #4
		ADD r0, r6, #0
		LDR r2, [pc, #0x94]
		LDR r1, [r7]
		BL       |sub_08046DD0|
		MOV r5, #0
|loc_08004D76|
		LSL r0, r5, #7
		ADD r0, r0, r4
		ADD r1, r5, #0
		BL       |inc_0x0158_0x143f2| + 0x4a68
		ADD r5, #1
		CMP r5, #3
		BLT      |loc_08004D76|
		MOV r2, #0x9f
		LDR r5, [r7]
		LSL r2, r2, #3
		ADD r1, r6, #0
		ADD r0, r5, #0
		BL       |sub_08046DD0|
		LDR r2, [pc, #0x70]
		MOV r0, #0x45
		LSL r0, r0, #5
		STR r2, [sp]
		ADD r2, r6, r0
		MOV r0, #0x9f
		LSL r0, r0, #3
		ADD r1, r6, r0
		MOV r3, #0x68
		ADD r0, r5, r0
		BL       |inc_0x046118_0x049114| + 0xf00
		MOV r1, #0x11
		LSL r1, r1, #7
		ADD r0, r5, r1
		ADD r1, r6, r1
		LDR r2, [r1, #0x20]
		LDR r1, [r1, #0x24]
		STR r1, [r0, #0x24]
		STR r2, [r0, #0x20]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x4bf8
