	CODE16
|sub_08015596|
|unk_08015596|
		CMP r2, #7
		BEQ      |inc_0x153f2_0x1a3f2| + 0x1ec
		CMP r2, #0x64
		BNE      |loc_080155C0|
		LDR r1, [pc, #0x200]
		MOV r3, #0
		MOV r2, #0x40
		SUB r1, #0xc
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r1, r6, #0
		LDR r0, [r4, #0x2c]
		BL       |inc_0x153f2_0x1a3f2| + 0xbf8
		LDR r0, [r4, #0x2c]
		LDR r1, [r0, #0x3c]
		STR r1, [r0, #0x40]
		ADD r0, r5, #0
		BL       |sub_08014d56|
|loc_080155C0|
|unk_080155C0|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
|loc_080155C4|
|unk_080155C4|
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		LDR r1, [sp, #8]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0
		BL       |inc_0x0158_0x143f2| + 0x14030
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		LDR r1, [sp, #8]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x1132
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
