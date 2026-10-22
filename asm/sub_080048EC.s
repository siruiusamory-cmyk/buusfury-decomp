	CODE16
|sub_080048EC|
|unk_080048EC|
		ADD r2, r6, #0
		MOV r1, #0
		ADD r0, r5, #0
		BL       |sub_0804912C|
		MOV r4, #0
		MOV r6, #0x9f
		LDR r7, [pc, #0x1f0]
		LSL r6, r6, #3
|loc_080048FE|
		LSL r0, r4, #3
		ADD r0, r0, r4
		LSL r0, r0, #1
		ADD r1, r0, r7
		MOV r0, #0x68
		MUL r0, r4
		ADD r0, r0, r5
		ADD r0, r0, r6
		BL       |loc_0801339C|
		ADD r4, #1
		CMP r4, #9
		BLT      |loc_080048FE|
		B        |inc_0x0158_0x143f2| + 0x478e
