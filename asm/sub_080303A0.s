	CODE16
|sub_080303A0|
|unk_080303A0|
		LDR r0, [pc, #0x9c]
		ADD r1, r5, #0
		STR r0, [r4]
		MOV r0, #0
		BL       |inc_0x301c0_0x311c0| + 0x834
		STR r0, [r4, #4]
		MOV r0, #0x78
		STR r0, [sp, #4]
		MOV r0, #0x94
		STR r0, [sp, #8]
		MOV r0, #0x98
		ADD r1, sp, #4
		BL       |sub_08030950|
		STR r0, [r4, #8]
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x1dc
