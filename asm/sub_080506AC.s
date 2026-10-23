	CODE16
|sub_080506AC|
|unk_080506AC|
		LDRB r5, [r6, #2]
		LDRB r0, [r6, #3]
		LDR r7, [pc, #0x54]
		MUL r5, r0
		LDR r0, [pc, #0x4c]
		ADD r1, r5, #0
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r7, #0x18]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080506D6|
		ADD r1, r5, #0
		LDR r0, [r7, #0x18]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r7, #0x18]
		BL       |loc_0801124C|
|loc_080506D6|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x30]
		LDR r3, [pc, #0x34]
		STR r0, [r4]
		STR r6, [r4, #0x28]
		LDR r1, [sp, #0xc]
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r1, [r4, #0x24]
		STR r2, [r4, #0x20]
		LDR r0, [sp, #0x10]
		STRB r0, [r4, #8]
		LDRB r2, [r6, #2]
		LDRB r0, [r6, #3]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r6, #8]
		LSL r0, r0, #5
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		B        |inc_0x049120_0x055620| + 0x7588
	CODE16
|dat_08050704|
	DCW      0x9680
	DCW      0x0804
	DCW      0x4fbc
	DCW      0x0805
|unk_0805070C|
	INCBIN	baserom.gba_0x5070c_0x5070e.extracted
|dat_0805070E|
	DCW      0x0804
	DCW      0x0000
	DCW      0x0601
