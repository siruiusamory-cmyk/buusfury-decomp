	CODE16
|sub_0800FF32|
|unk_0800FF32|
		LDR r1, [r0]
		LDR r3, [r4, #4]
		ASR r2, r1, #8
		CMP r2, r3
		BLT      |inc_0x0158_0x143f2| + 0xfdd6
		LSL r2, r3, #8
		SUB r1, r1, r2
		STR r1, [r0]
		B        |inc_0x0158_0x143f2| + 0xfdd6
