	CODE16
|sub_0800A560|
|unk_0800A560|
		LDR r0, [pc, #0x228]
		ADD r7, r4, #0
		LDR r5, [r0]
		ADD r7, #0x28
		ADD r5, #0x80
		MOV r2, #1
		ADD r0, r7, #0
		LDR r1, [r5, #0x28]
		BL       |loc_08009930|
		MOV r2, #1
		ADD r0, r7, #0
		LDR r1, [r5, #0x30]
		BL       |loc_08009930|
		ADD r0, r4, #0
|loc_0800A580|
|unk_0800A580|
		ADD r0, #0x38
		ADD r6, r0, #0
		LDR r1, [r5, #0x28]
		BL       |loc_08009324|
		ADD r4, r0, #0
		BNE      |loc_0800A590|
		ADD r6, r7, #0
|loc_0800A590|
		MOV r2, #0
		ADD r0, r6, #0
		LDR r1, [r5, #0x28]
		BL       |loc_08009930|
		MOV r2, #0
		ADD r0, r6, #0
		LDR r1, [r5, #0x30]
		BL       |loc_08009930|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xa404
