	CODE16
|sub_0803DB20|
|unk_0803DB20|
		LDR r1, [r4, #4]
		STR r1, [sp, #4]
		LDRH r1, [r5]
		CMP r1, #0
		BNE      |loc_0803DB3C|
		LDR r1, [r4, #4]
		ADD r0, r1, r0
		STR r0, [r4, #4]
		B        |loc_0803DB3C|
|loc_0803DB32|
|unk_0803DB32|
		ADD r0, #1
		LDR r1, [r4, #4]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [sp, #4]
|loc_0803DB3C|
|unk_0803DB3C|
		LDRH r1, [r7]
		ADD r7, #2
		CMP r1, #8
		BNE      |loc_0803DB4E|
		LDRH r0, [r7]
		ADD r7, #2
		SUB r6, #1
		STRB r0, [r4, #3]
		B        |loc_0803DB58|
|loc_0803DB4E|
		ADD r2, sp, #4
		ADD r0, r4, #0
		LDR r3, [r4, #0x20]
		BL       |inc_0x046118_0x049114| + 0x98e
|loc_0803DB58|
		SUB r6, #1
		CMP r6, #0
		DCW     0xDCEE
|loc_0803DB5E|
|unk_0803DB5E|
		LDRB r0, [r4]
		LSL r0, r0, #0x1d
		BMI      |loc_0803DB78|
		LDRH r0, [r5]
		CMP r0, #0
		BEQ      |loc_0803DB78|
		LDRB r1, [r4, #1]
		LDR r0, [r4, #8]
		ADD r7, r5, #2
		ADD r0, r0, r1
		STR r0, [r4, #8]
		ADD r5, r7, #0
		B        |sub_0803DAE8|
|loc_0803DB78|
		ADD sp, #0xc
		POP {r4, r5, r6, r7, pc}
