	CODE16
|sub_0801A1CE|
|unk_0801A1CE|
		LDR r1, [pc, #0x140]
		LDR r1, [r1, #0x14]
		LDR r1, [r1, #0xc]
		CMP r1, #0
		BNE      |loc_0801A1DC|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x4dda
|loc_0801A1DC|
		MOV r1, #0xa0
		BL       |inc_0x0158_0x143f2| + 0x13360
		B        |inc_0x153f2_0x1a3f2| + 0x4dda
