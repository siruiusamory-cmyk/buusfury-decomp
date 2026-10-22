	CODE16
|sub_0801C540|
|unk_0801C540|
		ADD r1, r4, #0
		ADD r1, #0x1e
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
|loc_0801C548|
		STRH r0, [r1]
		LDRH r2, [r1]
		CMP r2, r0
		BNE      |loc_0801C548|
		B        |inc_0x1c3f2_0x2ab4c| + 0x14c
