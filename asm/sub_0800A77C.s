	CODE16
|sub_0800A77C|
|unk_0800A77C|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xa120
		LDR r0, [pc, #0x14]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xa622
	INCBIN  baserom.gba_0xa78c_0xa78e.extracted
