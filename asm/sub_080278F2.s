	CODE16
|sub_080278F2|
|unk_080278F2|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_0802791C|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_0802791C|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_0802791C|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_0802791C|
		BL       |sub_0802770C|
		MOV r0, #1
		DCW     0xE7E9
|loc_0802791C|
		MOV r0, #0
		DCW     0xE7E7
|loc_08027920|
|unk_08027920|
; cited by 0x080276D0 (a pc-relative load targets 0x08027928)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E4
	INCBIN  baserom.gba_0x27926_0x27932.extracted
