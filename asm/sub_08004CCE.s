	CODE16
|sub_08004CCE|
|unk_08004CCE|
		SUB r1, #1
		BPL      |inc_0x0158_0x143f2| + 0x4b56
|loc_08004CD2|
|unk_08004CD2|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4b72
|loc_08004CD6|
|unk_08004CD6|
		ADD r1, #1
		CMP r4, r1
		BGT      |inc_0x0158_0x143f2| + 0x4b44
|loc_08004CDC|
|unk_08004CDC|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4b72
