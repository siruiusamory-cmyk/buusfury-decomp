	CODE16
|sub_080110FA|
|unk_080110FA|
		ADD r3, r6, #0
		ADD r0, r4, #0
		STR r5, [sp]
		LDR r2, [pc, #0xf0]
		LDR r1, [sp, #8]
		BL       |inc_0x0158_0x143f2| + 0xfc1c
		LDR r0, [pc, #0xec]
		ADD r1, r7, #0
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xb1
		BL       |inc_0x0158_0x143f2| + 0xa7e4
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x10f9e
