	CODE16
|loc_08042782|
		B        |loc_0804287A|
		MOV r7, #0x12
		CMP r4, #0
		BNE      |loc_080427A4|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x24f6
		CMP r0, #0
		BNE      |loc_080427A4|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BEQ      |loc_080427A2|
		LDRB r0, [r3, #8]
		CMP r0, #1
		BNE      |loc_080427A4|
|loc_080427A2|
		STRB r7, [r5, #4]
|loc_080427A4|
		LDRB r0, [r5, #0x10]
		LSL r0, r0, #1
		ADD r0, r0, r5
		LDRH r1, [r0, #0x34]
		CMP r1, #0
		BEQ      |loc_0804287A|
		SUB r1, #1
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
		STRH r1, [r0, #0x34]
		BNE      |loc_0804287A|
|loc_080427BA|
		STRB r7, [r5, #4]
		B        |loc_0804287A|
		CMP r4, #0
		BNE      |loc_0804287A|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x24f6
		CMP r0, #0
		BNE      |loc_0804287A|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BNE      |loc_080427DE|
		STRB r7, [r5, #4]
		MOV r0, #0x16
		STRB r0, [r5, #5]
		MOV r0, #0x32
		B        |loc_080427F0|
|loc_080427DE|
		MOV r7, #0
		STRB r7, [r5, #5]
		LDR r0, [pc, #0x3c8]
		STRB r7, [r5, #4]
		LDR r0, [r0]
		LDRB r0, [r0, #3]
		BL       |inc_0x042118_0x049114| + 0x1264
		MOV r0, #0x33
|loc_080427F0|
		STRH r0, [r5, #0x1e]
		LDRB r0, [r5, #0x10]
		MOV r7, #0
		LSL r0, r0, #1
		ADD r0, r0, r5
		STRH r7, [r0, #0x34]
		LDR r0, [sp, #0x20]
		STRB r7, [r0]
		STRB r7, [r5, #0xa]
		LDRH r0, [r5, #0x1e]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		MOV r1, #1
		BL       |loc_0804333c|
|loc_0804280E|
		STRH r7, [r5, #0x1e]
		B        |loc_0804287A|
		CMP r0, #0xf
		BNE      |loc_0804287A|
		STRB r0, [r5, #4]
		MOV r7, #1
		STRB r7, [r5, #2]
		MOV r1, #0
		MOV r0, #0x41
		BL       |loc_0804333c|
		ADD r1, r5, #0
		LDRB r0, [r5, #0x10]
		ADD r1, #0x20
		LDRB r2, [r1, #4]
		LSL r7, r0
		ORR r2, r7
		STRB r2, [r1, #4]
		LDRH r1, [r5, #0x26]
		LSL r0, r0, #1
		ADD r0, r0, r5
		STRH r1, [r0, #0x28]
		LDRB r1, [r5, #0x10]
		MOV r0, #4
		BL       |loc_080446a8|
		LDRB r0, [r5, #0x10]
		MOV r1, #0xe
		BL       |inc_0x042118_0x049114| + 0x28ce
		ADD r3, sp, #0
		STRB r0, [r3, #8]
		LDRB r0, [r3, #8]
		CMP r0, #0
		BEQ      |loc_0804287A|
		MOV r7, #0
		STRB r7, [r5, #5]
		STRB r7, [r5, #4]
		BL       |sub_08043368|
		LDR r0, [pc, #0x34c]
		LDR r0, [r0]
		LDRB r1, [r0, #2]
		LDRB r0, [r0, #3]
		ORR r0, r1
		BL       |inc_0x042118_0x049114| + 0x1264
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		MOV r1, #1
		STRH r0, [r5, #0x14]
		MOV r0, #0x25
		BL       |loc_0804333c|
