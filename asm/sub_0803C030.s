	CODE16
|sub_0803C030|
|unk_0803C030|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDR r2, [r0]
		LDR r3, [r5, #4]
		ADD r2, r2, r3
		STR r2, [r0]
		LDR r2, [r0, #4]
		LDR r1, [r5, #8]
		ADD r1, r2, r1
		STR r1, [r0, #4]
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x6e6e
