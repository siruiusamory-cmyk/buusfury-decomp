	CODE16
|loc_0800F49E|
|unk_0800F49E|
		LDR r0, [r4, #0x58]
		CMP r0, r2
		BNE      |loc_0800F4A8|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
|loc_0800F4A8|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
|loc_0800F4AC|
|unk_0800F4AC|
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0xf2e8
	INCBIN  baserom.gba_0xf4b0_0xf4b2.extracted
|sub_0800F4B2|
|unk_0800F4B2|
	INCBIN	baserom.gba_0xf4b2_0xf4b6.extracted
|dat_0800F4B6|
	DCW      0x0601
	DCW      0x1ba8
	DCW      0x0300
	DCW      0x25f0
	DCW      0x0807