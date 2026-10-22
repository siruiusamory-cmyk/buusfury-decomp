	CODE16
|sub_08010862|
|unk_08010862|
		STRB r1, [r4, #0x10]
		MOV r0, #8
		DCW     0xF02C
		DCW     0xFEA7
		CMP r0, #0
		BEQ      |loc_08010876|
		MOV r1, #3
		STRB r1, [r0, #4]
		LDR r1, [pc, #0x2d4]
		STR r1, [r0]
|loc_08010876|
		ADD r5, r0, #0
		MOV r1, #9
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
		B        |loc_0801085E|
		PUSH {r4, r5, lr}
		ADD r4, r1, #0
		ADD r1, #0xff
		ADD r1, #0xc1
		SUB sp, #0x7c
		MOV r0, #0
		STR r0, [r1, #0xc]
		MOV r0, #8
		DCW     0xF02C
		DCW     0xFE8D
		CMP r0, #0
		BEQ      |loc_080108AA|
		MOV r1, #5
		STRB r1, [r0, #4]
		LDR r1, [pc, #0x2a4]
		STR r1, [r0]
|loc_080108AA|
		ADD r5, r0, #0
		MOV r1, #0x11
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
		LDR r1, [r4]
		MOV r2, #0x88
		LDR r2, [r2, r1]
		MOV r5, #0
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		LDR r1, [pc, #0x274]
		SUB r1, #0x78
		CMP r0, #0
		LDR r0, [r1, #0x10]
		LDR r0, [r0, #4]
		BNE      |sub_080108E8|
		LDR r1, [pc, #0x274]
		ASR r0, r0, #1
		LDRB r1, [r1]
		ADD r1, #1
		CMP r0, r1
		BGE      |loc_080108F6|
		MOV r5, #1
		B        |loc_080108F6|
