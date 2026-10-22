	CODE16
|sub_080187B4|
|unk_080187B4|
		LDRB r2, [r1]
		MOV r3, #0x29
		LSL r3, r3, #4
		ADD r3, r0, r3
		STRB r2, [r3]
		LDR r2, [r0]
		LDR r3, [r2, #0x58]
		ADD r3, r3, r2
		BL       |inc_0x046118_0x049114| + 0x98e
		CMP r0, #0
		BEQ      |loc_080187D0|
		MOV r0, #2
		B        |inc_0x153f2_0x1a3f2| + 0x33c0
|loc_080187D0|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x33c0
