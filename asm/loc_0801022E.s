	CODE16
|loc_0801022E|
		MOV r0, #0
|loc_08010230|
		STR r0, [r4, #0x60]
		LDR r1, [pc, #0x9c]
		ADD r0, r4, #0
		LDR r1, [r1]
		LDR r2, [sp, #0x1c]
		ADD r1, #0x28
		LDR r3, [r1]
		ADD r0, #0x6c
		SUB r2, r2, r3
		LDR r3, [sp, #0x20]
		LDR r1, [r1, #4]
		STR r2, [sp, #0xc]
		SUB r1, r3, r1
		STR r1, [sp, #0x10]
		ADD r1, r2, #0
		LDR r2, [sp, #0x10]
		STMIA r0!, {r1, r2}
		LDR r0, [r4, #0x5c]
		CMP r0, #0
		BEQ      |loc_080102B8|
		ADD r6, r4, #0
		ADD r6, #0xff
		ADD r6, #0x41
		LDR r0, [r6, #0x38]
		ADD r1, sp, #0x14
		STR r0, [r5, #4]
		LDR r0, [pc, #0x68]
		LDRB r2, [r4, #8]
		LDR r0, [r0]
		BL       |inc_0x0158_0x143f2| + 0x984c
		LDR r1, [r6, #0x3c]
		MOV r3, #0xc
		ADD r1, r0, r1
		STR r1, [r5, #8]
		LDR r2, [sp, #0x1c]
		LDR r0, [r4, #0x58]
		LDRSB r6, [r0, r3]
		LDR r3, [r5, #4]
		ADD r2, r2, r6
		ADD r2, r2, r3
		MOV r3, #0xd
		LDRSB r0, [r0, r3]
		LDR r5, [sp, #0x20]
		LDR r3, [r4, #0x5c]
		ADD r0, r5, r0
		ADD r0, r0, r1
		LDRB r1, [r3]
		LDRB r3, [r3, #1]
		LDR r5, [r7, #8]
		ADD r1, r2, r1
		ADD r3, r0, r3
		CMP r2, r5
		BGE      |loc_080102B2|
		LDR r2, [r7]
		CMP r2, r1
		BGE      |loc_080102B2|
		LDR r1, [r7, #0xc]
		CMP r0, r1
		BGE      |loc_080102B2|
		LDR r0, [r7, #4]
		CMP r0, r3
		BGE      |loc_080102B2|
		MOV r0, #1
		B        |loc_080102B4|
|loc_080102B2|
		MOV r0, #0
|loc_080102B4|
		STR r0, [r4, #0x64]
		B        |loc_080102BA|
|loc_080102B8|
		STR r6, [r4, #0x64]
|loc_080102BA|
		LDR r0, [r4, #0x60]
		CMP r0, #0
		BNE      |loc_080102C6|
		LDR r0, [r4, #0x64]
		CMP r0, #0
		BEQ      |loc_080102CA|
|loc_080102C6|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0xff3c
|loc_080102CA|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xff3c
|sub_080102CE|
	DCW      0x0000
	DCW      0x2714
	DCW      0x0807
	DCW      0x0222
	DCW      0x0000
