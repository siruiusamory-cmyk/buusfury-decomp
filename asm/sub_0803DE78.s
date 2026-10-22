	CODE16
|sub_0803DE78|
|unk_0803DE78|
		CMP r4, #0x20
		BEQ      |loc_0803DE84|
		CMP r4, #0xa
		BEQ      |loc_0803DE84|
		CMP r4, #0xb
		BNE      |sub_0803DE88|
|loc_0803DE84|
		ADD r1, #2
		B        |inc_0x03d784_0x041118| + 0x6e8
