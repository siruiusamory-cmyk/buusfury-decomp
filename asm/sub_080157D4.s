	CODE16
|sub_080157D4|
|unk_080157D4|
		MOV r3, #0xff
		ADD r3, #0x31
		LDRB r3, [r3, r0]
		CMP r3, #1
		BNE      |loc_0801587E|
		ADD r7, r0, #0
		ADD r7, #0xff
		ADD r7, #1
		LDR r3, [r7, #0xc]
		LSL r1, r1, #0x1a
		LSL r3, r3, #2
		ADD r3, r3, r0
		ADD r4, r3, #0
		ADD r4, #0xff
		ADD r4, #0x35
		ADD r5, r4, #0
		STR r4, [sp, #4]
		ADD r4, r7, #0
		ADD r4, #0x40
		ADD r5, #0xc
		LSR r1, r1, #0x1f
		CMP r1, #0
		BEQ      |loc_08015826|
		ADD r1, r6, #0
		MOV r3, #0
		MOV r2, #0x40
		LDR r0, [sp, #8]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r5]
		LDR r1, [sp, #4]
		LDR r1, [r1]
		CMP r0, r1
		BLE      |loc_08015826|
		SUB r0, #1
		STR r0, [r5]
		LDR r0, [r4, #0x10]
		ADD r0, #1
		STR r0, [r4, #0x10]
		MOV r3, #0
		STR r3, [r7, #0x10]
|loc_08015826|
		LDR r2, [pc, #0xf8]
		LDR r0, [r2]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_0801587E|
		ADD r1, r6, #0
		MOV r6, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		LDR r0, [sp, #8]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r1, [r7, #0x2c]
		LDR r2, [pc, #0xdc]
		ADD r0, r1, #0
		LDR r1, [r1, #0x40]
		ADD r0, #0x4c
		LSL r3, r1, #1
		ADD r1, r3, r1
		LSL r1, r1, #2
		ADD r0, r1, r0
		LDR r0, [r0, #8]
		MOV r3, #0x68
		LDR r1, [r2, #0x10]
		MUL r0, r3
		ADD r0, r0, r1
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		BL       |loc_080135D2|
		LDR r1, [r5]
		CMP r0, r1
		BLE      |loc_0801587E|
		LDR r0, [r4, #0x10]
		CMP r0, #0
		BLE      |loc_0801587E|
		ADD r1, #1
		STR r1, [r5]
		LDR r0, [r4, #0x10]
		SUB r0, #1
		STR r0, [r4, #0x10]
		STR r6, [r7, #0x10]
|loc_0801587E|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x3de
