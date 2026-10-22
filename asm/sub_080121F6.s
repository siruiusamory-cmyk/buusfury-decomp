	CODE16
|sub_080121F6|
|unk_080121F6|
		MOV r6, #0
		ADD r1, r5, #0
		ADD r1, #8
		ADD r2, r7, #0
		STR r6, [sp, #8]
		STR r6, [sp, #0x4c]
		ADD r0, sp, #8
		BL       |loc_08004038|
		ADD r0, sp, #0xc
		STR r0, [sp, #4]
		ADD r0, r4, #0
		ADD r0, #8
		ADD r7, r0, #0
		LDR r1, [r5, #4]
		ADD r2, sp, #4
		BL       |sub_0803DB7C|
		STR r6, [sp, #4]
		LDRB r2, [r5, #3]
		ADD r1, r7, #0
		ADD r0, r4, #0
		LDR r3, [sp, #0x7c]
		BL       |sub_08012012|
		LDR r0, [pc, #0x19c]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x1209a
