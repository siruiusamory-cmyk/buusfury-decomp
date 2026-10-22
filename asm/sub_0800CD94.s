	CODE16
|sub_0800CD94|
|unk_0800CD94|
; cited by 0x0800CB38 (a pc-relative load targets 0x0800CDD0)
		ADD r2, r7, #0
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xc9bc
		LDR r0, [pc, #0x44]
		LDR r1, [pc, #0x3c]
		STR r0, [r4]
		STR r5, [r4, #0x5c]
		LDRH r0, [r5, #0x16]
		CMP r0, r1
		BNE      |loc_0800CDC2|
		LDR r0, [r5, #0x5c]
		LDR r0, [r0, #0x2c]
		LDR r1, [r0, #4]
		LDR r0, [pc, #0x20]
		LDR r0, [r0]
		BL       |loc_0801124C|
		STRH r0, [r5, #0x16]
		ADD r0, r5, #0
		BL       |sub_0800CD00|
|loc_0800CDC2|
		LDR r1, [r4, #0x20]
		LDRH r0, [r5, #0x16]
		LDRH r1, [r1, #0x14]
		ADD r0, r0, r1
		STRH r0, [r4, #0x16]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xcc3a
		DCD     0x0804E288
		DCD     0x08072578
	INCBIN  baserom.gba_0xcdd8_0xcde2.extracted
