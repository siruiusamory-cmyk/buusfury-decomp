	CODE16
|sub_080269BC|
|unk_080269BC|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #0x10
		DCW     0xD1F8
		LDR r5, [pc, #0x170]
		LDR r0, [r5]
		BL       |loc_080116FC|
		MOV r1, #0xff
		ADD r1, #1
		CMP r0, r1
|loc_080269D4|
|unk_080269D4|
		DCW     0xDBF0
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		ADD r0, r1, #0
		STR r1, [sp]
		LDR r1, [sp, #4]
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		LDRB r0, [r4, #0x10]
		ADD r1, r5, #4
		ADD r3, r4, #0
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #8]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0xc]
		LDR r0, [r0, #4]
		STR r1, [sp]
		ADD r0, r2, r0
		STR r0, [sp, #4]
		ADD r0, r1, #0
		LDR r1, [sp, #4]
		STR r0, [sp, #0x10]
		ADD r2, r6, #4
		STR r1, [sp, #0x14]
		ADD r1, sp, #0x10
		MOV r0, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x2f2
		ADD r1, r0, #0
		LDR r0, [r5]
		BL       |List_Append|
		DCW     0xE7C8
