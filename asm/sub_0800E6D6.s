	CODE16
|sub_0800E6D6|
|unk_0800E6D6|
		ADD r3, r5, #0
		ADD r2, r7, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |sub_0800E7F6|
		LDR r0, [pc, #0x68]
		STR r0, [r4]
		LDR r0, [pc, #0x68]
		LDR r1, [r0]
		ADD r2, r1, #1
		STR r2, [r0]
		LSL r1, r1, #2
		ADD r0, r1, r0
		STR r4, [r0, #4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xe57c
