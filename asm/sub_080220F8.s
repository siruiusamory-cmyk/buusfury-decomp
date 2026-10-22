	CODE16
|sub_080220F8|
|unk_080220F8|
		LDR r0, [pc, #0x1dc]
		MOV r1, #0xff
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0xc]
		ADD r1, #0xd1
		STR r6, [r1, r4]
		ADD r6, r4, #0
		ADD r5, r4, #0
		ADD r5, #0xc
		ADD r6, #0xff
		ADD r6, #0xd5
		STR r0, [r6]
		STR r7, [r4, #4]
		LDR r1, [sp, #8]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x607e
		LDR r7, [pc, #0x1c0]
		ADD r1, r0, #0
		STR r0, [r4, #8]
		LDR r0, [r7, #4]
		BL       |List_Append|
		LDR r0, [r6]
		LDR r2, [r4, #8]
		ADD r1, r0, #1
		LSL r0, r0, #2
		ADD r0, r0, r6
		STR r1, [r6]
		STR r2, [r0, #4]
		ADD r2, r5, #0
		MOV r1, #0x19
		LDR r0, [r7, #4]
		BL       |loc_08011C0C|
		ADD r1, r5, #0
		LDR r0, [r7, #8]
		BL       |sub_08012846|
		ADD r0, r4, #0
		DCW     0xE7D4
		BX       lr
