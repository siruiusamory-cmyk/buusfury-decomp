	CODE16
|loc_0803DC74|
		SUB r6, #1
		LDRB r0, [r3, r6]
		STRH r0, [r4]
		ADD r4, #2
		CMP r6, #0
		BNE      |loc_0803DC74|
