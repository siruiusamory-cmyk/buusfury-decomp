	CODE16
|sub_08020054|
|unk_08020054|
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0xc]
		LSL r0, r0, #7
		LDR r0, [r6, r0]
		CMP r0, #0
		BEQ      |loc_08020050|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDR r6, [pc, #0x218]
		LDR r0, [r6, #0x14]
		BL       |inc_0x0158_0x143f2| + 0x9528
		LDR r0, [pc, #0x218]
		LDR r1, [r4, #0xc]
		STR r1, [r0]
		LDR r0, [r6, #0x10]
		BL       |loc_080048A0|
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r5, r0
		LDR r0, [r0, #0x38]
		CMP r0, #0
		BNE      |loc_0802009C|
		BL       |inc_0x1c3f2_0x2ab4c| + 0x3114
		BL       |inc_0x03d784_0x041118| + 0xcc
		B        |loc_08020050|
|loc_0802009C|
		LDR r0, [r6, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_080200D8|
		MOV r0, #0xff
		ADD r0, #0x3d
		DCW     0xF01D
		DCW     0xFA81
		CMP r0, #0
		BEQ      |loc_080200D0|
		LDR r1, [pc, #0x1dc]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		LDR r1, [pc, #0x1cc]
		STR r1, [r0]
|loc_080200D0|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7BC
|loc_080200D8|
		MOV r0, #0xff
		ADD r0, #0x1d
		DCD     0xFA6CF01D
		CMP r0, #0
		DCW     0xD011
		LDR r1, [pc, #0x1b0]
		MOV r2, #0xff
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		ADD r2, #0x15
		STRB r7, [r2, r0]
		DCW     0xE001
|loc_080200FE|
|unk_080200FE|
		DCW     0xE052
|loc_08020100|
|unk_08020100|
		B        |loc_080201D8|
		LDR r2, [pc, #0x19c]
		STR r2, [r0]
		STR r7, [r1, #0x18]
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		BNE      |loc_0802019A|
		LDR r0, [pc, #0x190]
		DCW     0xF01D
		DCW     0xFA51
		ADD r4, r0, #0
		BEQ      |loc_08020190|
		LDR r0, [pc, #0x17c]
		STMIA r4!, {r0, r7}
		SUB r4, #8
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #1
		STR r7, [r0, #0xc]
		STR r7, [r0, #8]
		STR r7, [r0, #0x10]
		LDR r0, [pc, #0x178]
		STR r0, [r4]
		MOV r0, #0xff
		ADD r0, #0x95
		STR r7, [r0, r4]
		LDR r0, [pc, #0x174]
		ADD r0, r4, r0
		STR r7, [r0]
		LDR r0, [pc, #0x170]
		ADD r0, r4, r0
		BL       |loc_08004838|
		LDR r0, [pc, #0x16c]
		LDR r6, [pc, #0x170]
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r3, r6, #0
		ADD r0, #0x2e
		BL       |__vecmap1c__FPvT1iPFPv_v|
		LDR r7, [pc, #0x160]
		ADD r1, r5, #0
		ADD r1, #0x4c
		MOV r2, #4
		ADD r0, r5, #0
		ADD r3, r7, #0
		ADD r0, #0x3c
		BL       |__vecmap1c__FPvT1iPFPv_v|
		LDR r0, [pc, #0x150]
		ADD r3, r6, #0
		ADD r5, r4, r0
		ADD r1, r5, #0
		ADD r1, #0x3a
		ADD r0, r5, #0
		MOV r2, #2
		ADD r0, #0x2e
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r1, r5, #0
		ADD r1, #0x4c
		ADD r3, r7, #0
		MOV r2, #4
		ADD r0, r5, #0
		ADD r0, #0x3c
		BL       |__vecmap1c__FPvT1iPFPv_v|
|loc_08020190|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE75B
|loc_0802019A|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x7394
		BL       |inc_0x03d784_0x041118| + 0x29dc
		B        |loc_08020050|
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0xff
		ADD r0, #0x15
		DCW     0xF01D
		DCW     0xFA01
		CMP r0, #0
		BEQ      |loc_080201D0|
		LDR r1, [pc, #0xdc]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		LDR r1, [pc, #0xf4]
		STR r1, [r0]
|loc_080201D0|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE73C
