	CODE16
|sub_08012C80|
|unk_08012C80|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		B        |inc_0x0158_0x143f2| + 0x12b26
|loc_08012C90|
|unk_08012C90|
		ADD r0, r5, #0
		ADD r0, #0xff
		ADD r0, #0xb1
		CMP r1, #0x18
		BLT      |loc_08012CA2|
		STRB r6, [r0, #9]
		STRB r6, [r0, #8]
		B        |inc_0x0158_0x143f2| + 0x12b26
|loc_08012CA0|
		B        |loc_08012CAA|
