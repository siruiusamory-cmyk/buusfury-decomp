	CODE16
|loc_0800B042|
		LDR r0, [r4, #0x14]
		LDRH r1, [r0]
		CMP r1, #8
		BNE      |loc_0800B05C|
		LDRH r0, [r0, #2]
		STRB r0, [r5, #3]
		LDR r0, [r4, #0x14]
		ADD r0, #4
		STR r0, [r4, #0x14]
		LDR r1, [r4, #0x18]
		CMP r0, r1
		BNE      |loc_0800B042|
		B        |inc_0x0158_0x143f2| + 0xad74
|loc_0800B05C|
		LDRB r0, [r6, #4]
		LDRB r1, [r6, #5]
		STR r0, [r5, #4]
		STR r1, [r5, #8]
		LDR r0, [r4, #0x14]
		LDRH r1, [r0]
		ADD r0, r5, #0
		BL       |sub_0803DE50|
		LDR r2, [r4, #0x14]
		LDRH r0, [r2]
		LDR r1, [r5, #0xc]
		CMP r0, #0xff
		BLO      |loc_0800B07E|
		LDR r0, [r1, #4]
		ADD r0, #1
		B        |loc_0800B08A|
|loc_0800B07E|
		LDR r1, [r1]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		ADD r0, #1
|loc_0800B08A|
		LDRB r1, [r6, #4]
		ADD r0, r0, r1
		STRB r0, [r6, #4]
		ADD r2, #2
		STR r2, [r4, #0x14]
		B        |inc_0x0158_0x143f2| + 0xad74
	INCBIN  baserom.gba_0xb096_0xb0a8.extracted
