	CODE16
|sub_08028082|
|unk_08028082|
		MOV r6, #0x2c
		CMP r0, #5
		LDR r0, [r4, #0x18]
		BLT      |loc_080280C0|
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		SUB r0, #0x64
		STR r0, [sp, #0x104]
		ADD r0, #0x10
		STR r0, [sp, #0x10c]
		MOV r0, #0x3c
		STR r0, [sp, #0x110]
		ADD r0, r4, #0
		ADD r0, #0x68
		STR r6, [sp, #0x108]
		LDR r1, [r0, #0x28]
		LDR r0, [r0, #0x24]
		MUL r1, r6
		ADD r0, r1, r0
		LDR r1, [sp, #0x104]
		MOV r3, #0xa0
		ADD r1, r0, r1
		ADD r0, r5, #0
		ADD r2, sp, #0x104
		BL       |inc_0x03d784_0x041118| + 0x215e
		ADD r0, r4, #0
		BL       |loc_08027E48|
		B        |loc_080280FE|
|loc_080280C0|
		ADD r0, r0, r4
		ADD r0, #0x20
		LDRB r0, [r0, #4]
		LDR r1, [pc, #0x48]
		ADD r7, sp, #0x14
		ADD r1, #8
		LSL r0, r0, #2
		LDR r0, [r1, r0]
		LDR r1, [r0, #4]
		ADD r0, r7, #0
		BL       |inc_0x049120_0x055620|
		LDR r0, [r4, #0x18]
		ADD r1, r7, #0
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, #0x14
		STR r0, [sp, #4]
		ADD r0, #0x10
		STR r0, [sp, #0xc]
		MOV r0, #0x3c
		STR r0, [sp, #0x10]
		ADD r0, r5, #0
		STR r6, [sp, #8]
		ADD r2, sp, #4
		BL       |inc_0x03d784_0x041118| + 0x219e
		ADD r0, r4, #0
		BL       |loc_08027E48|
|loc_080280FE|
		LDR r0, [r4, #0x18]
		ADD r0, #1
		STR r0, [r4, #0x18]
		LDR r0, [r4, #0x20]
		STR r0, [r4, #0x1c]
		B        |loc_0802807E|
