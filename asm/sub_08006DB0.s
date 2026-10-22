	CODE16
|sub_08006DB0|
|unk_08006DB0|
		LDR r0, [pc, #0x60]
		STR r0, [r4]
		MOV r0, #0xff
		ADD r0, #1
		STR r0, [r4, #4]
		MOV r0, #8
		STR r0, [r4, #8]
		STR r5, [r4, #0xc]
		ADD r0, r5, #0
		BL       |Table_ClearSlot1|
		LDR r0, [pc, #0x50]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x6c56
