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
	CODE16
|dat_0802810A|
	DCW      0x0000
	DCW      0x0000
	DCW      0x0601
	DCW      0xea60
	DCW      0x0874
	DCW      0x7eb1
	DCW      0x0802
	DCW      0x1758
	DCW      0x0807
	DCW      0xbce8
	DCW      0x0806
	DCW      0x7eef
	DCW      0x0802
	DCW      0x7f75
	DCW      0x0802
	DCW      0x7fb9
	DCW      0x0802
	DCW      0x6941
	DCW      0x3101
	DCW      0x6141
	DCW      0x2908
	DCW      0xdb05
	DCW      0x498c
	DCW      0x6301
	DCW      0x2100
	DCW      0x6181
	DCW      0x2101
	DCW      0x61c1
|loc_08028142|
	DCW      0x4770
|loc_08028144|
	DCW      0xb5f8
	DCW      0x1c0f
	DCW      0x1c04
	DCW      0x2800
	DCW      0xd106
	DCW      0x209c
	DCW      0xf015
	DCW      0xfa32
	DCW      0x1c04
	DCW      0xd101
	DCW      0x1c20
	DCW      0xbdf8

