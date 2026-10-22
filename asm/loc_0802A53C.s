	CODE16
|loc_0802A53C|
		LDR r0, [r4, #0x14]
		ADD r0, #1
		ASR r2, r0, #2
		STR r0, [r4, #0x14]
		LDR r0, [r4, #0x18]
		CMP r0, r2
		BNE      |loc_0802A54C|
		DCW     0xE760
|loc_0802A54C|
|unk_0802A54C|
; cited by 0x0802A30A (a pc-relative load targets 0x0802A580)
		STR r2, [r4, #0x18]
		LDRH r0, [r4, #0xc]
		LSL r2, r2, #0x1f
		LSR r2, r2, #0x1f
		LSL r3, r2, #1
		LDR r5, [pc, #0x54]
		ADD r2, r3, r2
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		LSL r2, r2, #2
		ADD r1, r1, r2
		LDR r1, [r1, #8]
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x40
		LDR r1, [r1, #0x20]
		BL       |Thunk_VramCopy|
		DCW     0xE746
	INCBIN  baserom.gba_0x2a580_0x2a5a2.extracted
