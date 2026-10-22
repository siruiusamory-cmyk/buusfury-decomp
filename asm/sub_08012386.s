	CODE16
|sub_08012386|
|unk_08012386|
		LDR r0, [pc, #0x58]
		ADD r1, r5, #4
		STR r0, [r4]
		MOV r0, #0
		BL       |inc_0x301c0_0x311c0| + 0xa56
		ADD r1, r0, #0
		STR r0, [r4, #4]
		LDR r0, [pc, #0x4c]
		LDR r0, [r0, #4]
		BL       |List_Append|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x1222c
