	CODE16
|sub_08013D02|
|unk_08013D02|
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
|loc_08013D06|
		STRH r1, [r0]
		LDRH r2, [r0]
		CMP r2, r1
		BNE      |loc_08013D06|
