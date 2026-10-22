	CODE16
|sub_0801C664|
|unk_0801C664|
; cited by 0x0801C3FC (a pc-relative load targets 0x0801C6A0)
		LSR r0, r0, #4
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #0x10
		DCW     0xD1F8
		ADD r1, r4, #0
		ADD r5, sp, #4
		ADD r0, r5, #0
		BL       |sub_0804F944|
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0x48]
		LSL r0, r0, #3
		ADD r2, r0, r1
		ADD r1, r5, #0
		ADD r5, sp, #0xc
		ADD r0, r5, #0
		BL       |inc_0x049120_0x055620| + 0x9e94
		ADD r2, r4, #0
		ADD r1, r5, #0
		MOV r0, #0
		BL       |loc_080383D4|
		ADD r1, r0, #0
		LDR r0, [pc, #8]
		LDR r0, [r0, #4]
		BL       |List_Append|
		DCW     0xE7DF
		DCD     0x0871DD38
	INCBIN  baserom.gba_0x1c6a4_0x1c6c6.extracted
