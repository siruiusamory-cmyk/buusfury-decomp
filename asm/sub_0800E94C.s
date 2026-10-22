	CODE16
|sub_0800E94C|
|unk_0800E94C|
		STR r0, [r4, #0x14]
		LDR r2, [r6]
		MOV r0, sp
		CMP r2, #0
		BEQ      |sub_0800E960|
		MOV r3, #1
		MOV r2, #4
		BL       |sub_0800AD3E|
		B        |inc_0x0158_0x143f2| + 0xe810
