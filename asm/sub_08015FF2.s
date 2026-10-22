	CODE16
|sub_08015FF2|
|unk_08015FF2|
		LDR r2, [r0, #0x20]
		CMP r2, r1
		BNE      |loc_08015FFA|
		B        |inc_0x153f2_0x1a3f2| + 0xb2a
|loc_08015FFA|
		BX       lr
