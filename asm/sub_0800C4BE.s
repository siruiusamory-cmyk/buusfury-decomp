	CODE16
|sub_0800C4BE|
|unk_0800C4BE|
		LDR r1, [r0, #0x24]
		ADD r1, #1
		STR r1, [r0, #0x24]
		LDR r1, [r0, #0x28]
		ADD r1, #2
		STR r1, [r0, #0x28]
		LDR r2, [r0, #0x1c]
		LDR r3, [r0, #0x24]
		ADD r2, r2, r3
		STR r2, [r0, #0x1c]
		LDR r2, [r0, #0x20]
		ADD r1, r2, r1
		STR r1, [r0, #0x20]
		B        |inc_0x0158_0x143f2| + 0xc364
