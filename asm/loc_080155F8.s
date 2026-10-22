	CODE16
|loc_080155F8|
|unk_080155F8|
		MOV r0, #0
		BL       |inc_0x0158_0x143f2| + 0x14030
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
|loc_08015606|
|unk_08015606|
		MOV r0, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x1132
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
|loc_08015614|
|unk_08015614|
		B        |inc_0x153f2_0x1a3f2| + 0x22a
|loc_08015616|
|unk_08015616|
		B        |inc_0x153f2_0x1a3f2| + 0x35c
|loc_08015618|
|unk_08015618|
		STR r6, [r4, #0x10]
		B        |loc_080155C0|
		LDR r1, [sp, #4]
		ADD r6, r5, #0
		LDRB r0, [r1]
		ADD r6, #0xff
		ADD r6, #0x41
		CMP r0, #0
		BEQ      |loc_08015672|
		CMP r0, #1
		BNE      |loc_080156F0|
		ADD r0, r5, #0
		LDR r1, [r4, #0x28]
		BL       |inc_0x0158_0x143f2| + 0x6514
		MOV r0, #0
		STR r0, [r4, #0xc]
		LDR r1, [sp, #4]
		STRB r0, [r1]
		LDR r0, [r4, #0x1c]
		MOV r1, #1
		STR r1, [r0, #8]
		LDR r1, [r4, #0x2c]
		ADD r0, r1, #0
		LDR r1, [r1, #0x40]
		ADD r0, #0x4c
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r1, r0
		LDR r0, [r0, #8]
		MOV r3, #0x68
		LDR r1, [pc, #0x140]
		MUL r0, r3
		LDR r1, [r1, #0x10]
		LDR r2, [r6, #4]
		ADD r0, r0, r1
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		ADD r1, r0, #0
		ADD r1, #0x28
		LSL r2, r2, #0x18
		LSR r2, r2, #0x18
		B        |loc_080156F2|
|loc_08015672|
		MOV r0, #1
		STR r0, [r4, #0xc]
		ADD r1, r5, #0
		MOV r0, #0
		BL       |loc_08016208|
		ADD r1, r0, #0
		STR r0, [r4, #0x28]
		ADD r0, r5, #0
		BL       |loc_0800664E|
		LDR r1, [sp, #4]
		MOV r0, #1
		STRB r0, [r1]
		LDR r0, [r4, #0x1c]
		MOV r2, #0
		STR r2, [r0, #8]
		LDR r1, [r4, #0x2c]
		ADD r0, r1, #0
		LDR r1, [r1, #0x40]
		ADD r0, #0x4c
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r1, r0
		LDR r0, [r0, #8]
		MOV r3, #0x68
		LDR r1, [pc, #0xf0]
		MUL r0, r3
		LDR r1, [r1, #0x10]
		ADD r0, r0, r1
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		ADD r1, r0, #0
		ADD r1, #0x2c
		LDRH r3, [r1]
		STR r3, [r4, #0x34]
		LDRH r1, [r1]
		STR r1, [r6, #0x10]
		ADD r1, r0, #0
		ADD r1, #0x28
		LDRB r3, [r1]
		STR r3, [r4, #0x38]
		LDRB r1, [r1]
		STR r1, [r6, #4]
		ADD r1, r0, #0
		ADD r1, #0x29
		LDRB r3, [r1]
		STR r3, [r4, #0x3c]
		LDRB r1, [r1]
		ADD r0, #0x2a
		STR r1, [r6, #8]
		LDRB r1, [r0]
		STR r1, [r6]
		LDRB r0, [r0]
		STR r0, [r6, #0xc]
		ADD r3, r2, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		LDR r1, [sp, #8]
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_080156F0|
		B        |loc_08015742|
|loc_080156F2|
		STRB r2, [r1]
		LDRB r3, [r1]
		CMP r3, r2
		BNE      |loc_080156F2|
		LDR r2, [r6, #8]
		ADD r1, r0, #0
		ADD r1, #0x29
		LSL r2, r2, #0x18
		LSR r2, r2, #0x18
|loc_08015704|
		STRB r2, [r1]
		LDRB r3, [r1]
		CMP r3, r2
		BNE      |loc_08015704|
		LDR r2, [r6, #0xc]
		ADD r1, r0, #0
		ADD r1, #0x2a
		LSL r2, r2, #0x18
		LSR r2, r2, #0x18
|loc_08015716|
		STRB r2, [r1]
		LDRB r3, [r1]
		CMP r3, r2
		BNE      |loc_08015716|
		LDR r2, [r6, #0x10]
		ADD r1, r0, #0
		ADD r1, #0x2c
		LSL r2, r2, #0x10
		LSR r2, r2, #0x10
|loc_08015728|
		STRH r2, [r1]
		LDRH r3, [r1]
		CMP r3, r2
		BNE      |loc_08015728|
		BL       |loc_08013C66|
		LDR r1, [pc, #0x68]
		MOV r3, #0
		MOV r2, #0x40
		ADD r1, #0xc
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08015742|
		ADD r0, r5, #0
		BL       |sub_08014d56|
		MOV r2, #0
		STR r2, [r4, #0x10]
|loc_0801574C|
		B        |loc_080155C0|
		MOV r6, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		LDR r1, [sp, #8]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r1, [sp, #4]
		LDRB r0, [r1]
		CMP r0, #0
		BEQ      |loc_08015788|
		CMP r0, #1
		BNE      |loc_0801574C|
		LDR r1, [sp, #4]
		STRB r6, [r1]
		LDR r0, [r4, #0x1c]
		MOV r1, #1
		STR r1, [r0, #8]
		LDR r1, [r4, #0x28]
		ADD r0, r5, #0
		BL       |inc_0x0158_0x143f2| + 0x6514
		ADD r0, r5, #0
		STR r6, [r4, #0xc]
		BL       |sub_08014d56|
		MOV r0, #0
		STR r6, [r4, #0x10]
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
|loc_08015788|
		MOV r0, #1
		BL       |inc_0x03d784_0x041118| + 0xf2
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x1a0
