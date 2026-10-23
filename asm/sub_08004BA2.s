	CODE16
|sub_08004BA2|
|unk_08004BA2|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4a46
|loc_08004BA6|
|unk_08004BA6|
		ADD r0, #1
		CMP r7, r0
		BGT      |inc_0x0158_0x143f2| + 0x4a1a
|loc_08004BAC|
|unk_08004BAC|
		ADD r4, #1
		CMP ip, r4
		BGT      |inc_0x0158_0x143f2| + 0x4a0c
|loc_08004BB2|
|unk_08004BB2|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4a46
|sub_08004BB6|
	DCW      0x0000
	DCW      0x55a4
	DCW      0x0805
	DCW      0xca24
	DCW      0x0874
