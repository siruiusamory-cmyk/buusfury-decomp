	CODE16
|sub_0802BD6A|
|unk_0802BD6A|
		ADD r2, r6, #0
		MOV r6, sp
		ADD r1, r5, #0
		MOV r0, sp
		BL       |inc_0x0158_0x143f2| + 0xd8ce
		ADD r2, r6, #0
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800D960|
		LDR r0, [pc, #0x40]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x30]
		MOV r0, #0x28
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x21a
