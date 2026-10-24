	CODE16
|loc_0800FC16|
|unk_0800FC16|
		B        |loc_0800FD24|
|loc_0800FC18|
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xfb32
		LDR r0, [sp, #0x70]
		LDR r1, [r6, #0xc]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xfb32
		ADD r1, r5, #0
		ADD r1, #0x14
		ADD r6, r1, #0
		ADD r0, r4, #0
		BL       |Battle_ComputeDamage|
		ADD r0, r5, #0
		ADD r0, #0x2c
		B        |inc_0x0158_0x143f2| + 0xfae0
