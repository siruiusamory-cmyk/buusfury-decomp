	CODE16
|sub_08019032|
|unk_08019032|
		AND r5, r0
		LDR r0, [r6, #0xc]
		ADD r4, #1
		CMP r0, r4
		BGT      |inc_0x153f2_0x1a3f2| + 0x3c28
|loc_0801903C|
|unk_0801903C|
		LSL r0, r5, #0x18
		LSR r0, r0, #0x18
		B        |inc_0x153f2_0x1a3f2| + 0x3c3c
