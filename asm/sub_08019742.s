	CODE16
|sub_08019742|
|unk_08019742|
		CMP r3, #0x13
		BEQ      |inc_0x153f2_0x1a3f2| + 0x4388
		CMP r3, #0x20
		BNE      |loc_08019788|
		STR r2, [r0, #0x10]
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x434e
|loc_08019750|
|unk_08019750|
		LDR r1, [r0]
		LDR r2, [r1, #8]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x434e
|loc_0801975E|
|unk_0801975E|
		MOV r1, #0xff
		STRB r1, [r0, #0x14]
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x434e
|loc_08019766|
|unk_08019766|
		LDR r1, [r0, #0x10]
		CMP r1, r2
		BNE      |loc_08019776|
		ADD r1, r0, #0
		LDR r0, [pc, #0x2c]
		LDR r0, [r0]
		BL       |loc_08011944|
|loc_08019776|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x434e
		MOV r2, #0xff
		STRB r2, [r0, #0x17]
		LDRB r2, [r0, #0x14]
		STRB r2, [r0, #0x15]
		STR r1, [r0, #0x10]
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x434e
