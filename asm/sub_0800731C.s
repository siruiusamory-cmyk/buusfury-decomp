	CODE16
|sub_0800731C|
|unk_0800731C|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #0x90]
		STR r0, [r4]
		LDR r0, [r5, #0x10]
		STR r0, [r4, #0x10]
		MOV r0, #0
		STR r0, [r4, #0x14]
		STR r0, [r4, #0x18]
		STR r0, [r4, #0x1c]
		STR r0, [r4, #0x20]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x71c2
