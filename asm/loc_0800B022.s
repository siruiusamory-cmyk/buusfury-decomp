	CODE16
|loc_0800B022|
		LDR r0, [r4, #0x14]
		LDR r1, [r4, #0x18]
		CMP r0, r1
		BNE      |loc_0800B02C|
		B        |inc_0x0158_0x143f2| + 0xad74
|loc_0800B02C|
		B        |loc_0800B042|
		LDR r0, [sp, #4]
		CMP r0, #0
		LDR r0, [r4, #0x4c]
		LDR r0, [r0, #8]
		BEQ      |loc_0800B03E|
		ADD r0, #0x14
		STRB r0, [r6, #4]
		B        |inc_0x0158_0x143f2| + 0xae9a
|loc_0800B03E|
		STRB r0, [r6, #4]
		B        |loc_0800B00C|
