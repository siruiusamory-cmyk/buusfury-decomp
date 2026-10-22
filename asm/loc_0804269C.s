	CODE16
|loc_0804269C|
|unk_0804269C|
		B        |loc_08042782|
	INCBIN  baserom.gba_0x4269e_0x426c4.extracted
		CMP r4, #0
		BNE      |loc_08042782|
		MOV r0, #0xd
		STRB r0, [r5, #5]
		STRB r0, [r5, #4]
		B        |loc_08042782|
|unk_080426D0|
		MOV r7, #0xe
		CMP r4, #0
		BNE      |loc_080426EA|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x1ea4
		CMP r0, #0
		BNE      |loc_080426EA|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BNE      |loc_080426EA|
		STRB r7, [r5, #4]
|loc_080426EA|
		LDRH r0, [r5, #0x1a]
		CMP r0, #0
		BEQ      |loc_08042782|
		SUB r0, #1
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STRH r0, [r5, #0x1a]
		BNE      |loc_08042782|
		B        |loc_080427BA|
		CMP r4, #0
		BNE      |loc_08042782|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x1ea4
		CMP r0, #0
		BNE      |loc_08042782|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BNE      |loc_08042722|
		STRB r7, [r5, #4]
		MOV r0, #0xf
		STRB r0, [r5, #5]
		MOV r0, #0x22
		STRH r0, [r5, #0x1e]
		LDRB r0, [r5, #0x10]
		STRH r0, [r5, #0x14]
		B        |loc_08042740|
|loc_08042722|
		MOV r7, #0
		STRB r7, [r5, #5]
		STRB r7, [r5, #4]
		MOV r0, #0x23
		STRH r0, [r5, #0x1e]
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		STRH r0, [r5, #0x14]
		LDRB r0, [r5, #7]
		CMP r0, #0
		BEQ      |loc_08042740|
		MOV r0, #3
		STRB r0, [r5, #7]
		MOV r0, #9
		STRB r0, [r5, #4]
|loc_08042740|
		LDRH r0, [r5, #0x1e]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		MOV r1, #1
		BL       |loc_0804333c|
		MOV r7, #0
		B        |loc_0804280E|
		CMP r4, #0
		BNE      |loc_08042782|
		MOV r0, ip
		LDRB r0, [r0, #3]
		MOV r7, #0
		ADD r3, r5, #0
		STRH r0, [r5, #0x14]
		MOV r0, #0x11
		STRB r0, [r5, #5]
		STRB r0, [r5, #4]
		STRB r7, [r5, #0x10]
		MOV r7, #1
|loc_08042768|
		MOV r0, ip
		LDRB r1, [r0, #3]
		LDRB r0, [r3, #0x10]
		ADD r2, r7, #0
		LSL r2, r0
		AND r1, r2
		BNE      |loc_08042782|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r3, #0x10]
		CMP r0, #4
		BLO      |loc_08042768|
