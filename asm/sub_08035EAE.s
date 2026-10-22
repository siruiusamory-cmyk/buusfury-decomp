	CODE16
|sub_08035EAE|
|unk_08035EAE|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		ADD r0, r4, #0
		LDR r1, [sp, #4]
		LDR r2, [sp, #8]
		ADD r0, #0xff
		ADD r0, #0xa1
		LSL r1, r1, #8
		ADD r2, #0x10
		LSL r2, r2, #8
		STMIA r0!, {r1}
		STR r2, [r0]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0xcea
