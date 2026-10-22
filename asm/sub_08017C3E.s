	CODE16
|sub_08017C3E|
|unk_08017C3E|
		ADD r3, r5, #0
		ADD r2, r7, #0
		ADD r0, r4, #0
		STR r6, [sp]
		LDR r1, [sp, #0x18]
		BL       |inc_0x0158_0x143f2| + 0x10f80
		LDR r0, [pc, #0x200]
		MOV r1, #0xff
		STR r0, [r4]
		MOV r0, #0
		ADD r1, #0xbd
		STRH r0, [r1, r4]
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r2, [sp, #0x1c]
		STR r0, [r1]
		STR r2, [r1, #0x10]
		STR r0, [r1, #4]
		STR r0, [r1, #8]
		STR r0, [r1, #0xc]
		LDR r0, [pc, #0x1e8]
		ADD r1, r4, #0
		LDR r5, [r0]
		ADD r0, sp, #4
		BL       |Object_WriteBounds1|
		ADD r5, #0x80
		LDR r1, [r5, #0x28]
		MOV r2, #0
		ADD r0, sp, #4
		BL       |loc_08009930|
		MOV r2, #0
		ADD r0, sp, #4
		LDR r1, [r5, #0x30]
		BL       |loc_08009930|
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2848
