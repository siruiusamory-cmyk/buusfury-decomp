	CODE16
|sub_08008DE6|
|unk_08008DE6|
		ADD r2, r5, #0
		ADD r1, r0, #0
		MOV r3, #1
		MOV r0, #0
		BL       |loc_080109AA|
		ADD r5, r0, #0
		MOV r0, #8
		DCW     0xF034
		DCW     0xFBDF
		CMP r0, #0
		BEQ      |loc_08008E04|
		LDR r1, [pc, #0x224]
		STMIA r0!, {r1, r5}
		SUB r0, #8
|loc_08008E04|
		ADD r1, r0, #0
		LDR r0, [r7, #0x20]
		BL       |loc_08021094|
		ADD r1, r5, #0
		LDR r0, [r7, #0x14]
		BL       |List_Append|
		LDR r0, [r7, #8]
		LDRB r0, [r0, #1]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |sub_08008E2C|
		MOV r0, #0
		BL       |loc_0800B854|
		ADD r1, r0, #0
		LDR r0, [r7, #0x14]
		BL       |List_Append|
