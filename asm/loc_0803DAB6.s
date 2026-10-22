	CODE16
|loc_0803DAB6|
|unk_0803DAB6|
		LDRH r1, [r4]
		ADD r4, #2
		CMP r1, #8
		BNE      |sub_0803DAC8|
		LDRH r0, [r4]
		ADD r4, #2
		SUB r5, #1
		STRB r0, [r6, #3]
		B        |inc_0x03d784_0x041118| + 0x34e
