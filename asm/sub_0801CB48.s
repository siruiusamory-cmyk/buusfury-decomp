	CODE16
|sub_0801CB48|
|unk_0801CB48|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0801CB72|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0801CB72|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0801CB72|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0801CB72|
		BL       |sub_0801C978|
		MOV r0, #1
		DCW     0xE7E9
|loc_0801CB72|
		MOV r0, #0
		DCW     0xE7E7
|loc_0801CB76|
|unk_0801CB76|
; cited by 0x0801C928 (a pc-relative load targets 0x0801CB7C)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E4
	INCBIN  baserom.gba_0x1cb7c_0x1cb86.extracted
