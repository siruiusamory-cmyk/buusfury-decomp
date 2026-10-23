	CODE16
|loc_08028962|
		LDR r0, [r4, #0x14]
		ADD r0, #1
		ASR r2, r0, #2
		STR r0, [r4, #0x14]
		LDR r0, [r4, #0x18]
		CMP r0, r2
		BNE      |loc_08028972|
		DCW     0xE73B
|loc_08028972|
		STR r2, [r4, #0x18]
		LDRH r0, [r4, #0xc]
		LSL r2, r2, #0x1f
		LSR r2, r2, #0x1f
		LSL r6, r2, #1
		LDR r5, [pc, #0x64]
		ADD r6, r6, r2
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		LSL r6, r6, #2
		ADD r1, r1, r6
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
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x48]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x80
		ADD r1, r1, r6
		LDR r1, [r1, #0x2c]
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		DCW     0xE717
	INCBIN  baserom.gba_0x289ba_0x289de.extracted
|sub_080289DE|
	DCW      0x0804
	DCW      0x2fe4
	DCW      0x0300
	DCW      0x0000
	DCW      0x0601
