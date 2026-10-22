	CODE16
|sub_0800B140|
|unk_0800B140|
		SUB r5, r1, #3
|loc_0800B142|
|unk_0800B142|
		ADD r0, r4, #0
		BL       |sub_0800AE74|
		SUB r5, #1
		DCW     0xD1FA
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xac48
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xafe6
