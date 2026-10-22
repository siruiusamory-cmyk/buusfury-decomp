	CODE16
|sub_08008A1E|
|unk_08008A1E|
		ADD r1, #0x38
		ADD r2, #1
		CMP r2, r0
		BLT      |inc_0x0158_0x143f2| + 0x88b6
|loc_08008A26|
|unk_08008A26|
		MOV r3, #0
		MOV r2, #0x3a
		ADR      r1, |inc_0x0158_0x143f2| + 0x8904
		ADR      r0, |inc_0x0158_0x143f2| + 0x891c
		BL       |Irq_WriteMaster1|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x88c4
