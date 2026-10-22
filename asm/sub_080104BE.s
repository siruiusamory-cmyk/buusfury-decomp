	CODE16
|sub_080104BE|
|unk_080104BE|
		MOV r1, #0x7f
		MVN r1, r1
		CMP r0, r1
		BGE      |loc_080104DC|
		MOV r1, #0x10
		ADD r0, r5, #0
		BL       |Record_SelectIndexed|
		LDR r0, [r4, #4]
		MOV r2, #0
		CMP r0, #0
		BNE      |loc_080104D8|
		MOV r2, #3
|loc_080104D8|
		STRB r2, [r5, #0x10]
		B        |inc_0x0158_0x143f2| + 0x10364
|loc_080104DC|
		MOV r1, #0xf
		ADD r0, r5, #0
		BL       |Record_SelectIndexed|
		LDR r0, [r4, #4]
		MOV r2, #1
		CMP r0, #0
		BEQ      |loc_080104EE|
		MOV r2, #0
|loc_080104EE|
		STRB r2, [r5, #0x10]
		B        |inc_0x0158_0x143f2| + 0x10364
