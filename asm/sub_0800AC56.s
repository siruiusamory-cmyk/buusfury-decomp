	CODE16
|sub_0800AC56|
|unk_0800AC56|
		LDR r1, [r0, #0x24]
		SUB r1, #4
		STR r1, [r0, #0x24]
		ASR r1, r1, #3
		ADD r1, #8
		STR r1, [r0, #4]
		B        |inc_0x0158_0x143f2| + 0xaafc
