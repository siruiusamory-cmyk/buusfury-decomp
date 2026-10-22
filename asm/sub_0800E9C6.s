	CODE16
|sub_0800E9C6|
|unk_0800E9C6|
		MOV r3, #0
		MOV r2, #6
		STR r0, [r4, #0x1c]
		ADD r0, sp, #4
		ADD r1, r5, #0
		BL       |sub_0800AD3E|
		STR r0, [r4, #0x20]
		B        |inc_0x0158_0x143f2| + 0xe86a
