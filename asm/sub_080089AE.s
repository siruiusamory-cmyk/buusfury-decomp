	CODE16
|sub_080089AE|
|unk_080089AE|
		LDR r1, [r0, #0x28]
		CMP r1, #0
		BNE      |loc_080089B8|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x8852
|loc_080089B8|
		LDR r1, [r0, #0x28]
		MOV r0, #0
		STR r0, [sp]
		STR r0, [sp, #0x44]
		MOV r0, sp
		MOV r2, #0
		BL       |loc_08004038|
		LDR r0, [sp, #4]
		B        |inc_0x0158_0x143f2| + 0x8852
