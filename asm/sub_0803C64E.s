	CODE16
|sub_0803C64E|
|unk_0803C64E|
		CMP r0, #0x10
		BNE      |inc_0x351c0_0x3d4d0| + 0x748a
		LDR r0, [r4, #0x14]
		LSL r0, r0, #1
		ADD r0, #1
		STRB r0, [r5, #0x11]
		B        |inc_0x351c0_0x3d4d0| + 0x748a
