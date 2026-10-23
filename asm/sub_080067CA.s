	CODE16
|sub_080067CA|
|unk_080067CA|
		LDR r0, [r5, #4]
		ADD r4, #1
		CMP r0, r4
		BGT      |inc_0x0158_0x143f2| + 0x6658
|loc_080067D2|
|unk_080067D2|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x6670
|sub_080067D6|
	DCW      0x1c01
	DCW      0x31ff
	DCW      0x3101
