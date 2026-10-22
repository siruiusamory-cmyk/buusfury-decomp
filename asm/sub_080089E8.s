	CODE16
|sub_080089E8|
|unk_080089E8|
		LDR r1, [r0, #0x24]
		MOV r0, #0
		STR r0, [sp]
		STR r0, [sp, #0x44]
		MOV r0, sp
		MOV r2, #0
		BL       |loc_08004038|
		LDR r0, [sp, #4]
		B        |inc_0x0158_0x143f2| + 0x888c
