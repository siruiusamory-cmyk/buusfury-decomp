	CODE16
|sub_08006DEE|
|unk_08006DEE|
		LDR r0, [pc, #0x2c]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #4]
		MOV r0, #8
		STR r0, [r4, #8]
		STR r5, [r4, #0xc]
		ADD r0, r5, #0
		BL       |Table_ClearSlot1|
		LDR r0, [pc, #0x1c]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x6c94
