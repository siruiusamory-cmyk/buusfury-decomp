	CODE16
|sub_0801A226|
|unk_0801A226|
		LDR r1, [pc, #0xfc]
		LDR r1, [r1]
		CMP r1, #0
		BEQ      |loc_0801A232|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x4e32
|loc_0801A232|
		MOV r1, #0x28
|loc_0801A234|
|unk_0801A234|
		BL       |inc_0x0158_0x143f2| + 0x13360
		B        |inc_0x153f2_0x1a3f2| + 0x4e32
	INCBIN  baserom.gba_0x1a23a_0x1a2aa.extracted
