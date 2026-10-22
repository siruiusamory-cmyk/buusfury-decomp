	CODE16
|sub_08013D22|
|unk_08013D22|
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
|loc_08013D26|
		STRH r1, [r0]
		LDRH r2, [r0]
		CMP r2, r1
		BNE      |loc_08013D26|
|loc_08013D2E|
|unk_08013D2E|
		ADD r0, r5, #0
		LDR r1, [r4, #0x1c]
		ADD r0, #0x50
		CMP r1, #0
		BGE      |loc_08013D42|
|loc_08013D38|
		STRH r7, [r0]
		LDRH r1, [r0]
		CMP r1, r7
		BNE      |loc_08013D38|
		B        |loc_08013D4E|
|loc_08013D42|
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
|loc_08013D46|
		STRH r1, [r0]
		LDRH r2, [r0]
		CMP r2, r1
		BNE      |loc_08013D46|
|loc_08013D4E|
		ADD r0, r5, #0
		LDR r1, [r4, #0x20]
		ADD r0, #0x52
		CMP r1, #0
		BGE      |loc_08013D62|
|loc_08013D58|
		STRH r7, [r0]
		LDRH r1, [r0]
		CMP r1, r7
		BNE      |loc_08013D58|
		B        |loc_08013D6E|
|loc_08013D62|
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
|loc_08013D66|
		STRH r1, [r0]
		LDRH r2, [r0]
		CMP r2, r1
		BNE      |loc_08013D66|
|loc_08013D6E|
		ADD r0, r5, #0
		LDR r1, [r4, #0x24]
		ADD r0, #0x54
		CMP r1, #0
		BGE      |sub_08013D84|
		ADD r1, r7, #0
|loc_08013D7A|
		STRH r1, [r0]
		LDRH r2, [r0]
		CMP r2, r1
		BNE      |loc_08013D7A|
		B        |inc_0x0158_0x143f2| + 0x13c38
