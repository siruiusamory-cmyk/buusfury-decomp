	CODE16
|sub_08004850|
|unk_08004850|
		MOV r1, #0xe4
		MOV r0, #0
		STR r0, [r1, r4]
		MOV r0, #0x45
		LSL r0, r0, #5
		MOV r6, #0x9f
		LSL r6, r6, #3
		ADD r1, r4, r0
		MOV r2, #0x68
		ADD r0, r4, r6
		LDR r3, [pc, #0x280]
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r2, r5, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |sub_0804912C|
		LDR r7, [pc, #0x274]
		MOV r5, #0
|loc_08004878|
		LSL r0, r5, #3
		ADD r0, r0, r5
		LSL r0, r0, #1
		ADD r1, r0, r7
		MOV r0, #0x68
		MUL r0, r5
		ADD r0, r0, r4
		ADD r0, r0, r6
		BL       |Stats_LoadRecord|
		ADD r5, #1
		CMP r5, #9
		BLT      |loc_08004878|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x46f6
