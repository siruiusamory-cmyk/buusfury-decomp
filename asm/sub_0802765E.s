	CODE16
|sub_0802765E|
|unk_0802765E|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_08027688|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_08027688|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_08027688|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_08027688|
		BL       |sub_08027516|
		MOV r0, #1
		DCW     0xE7E9
|loc_08027688|
		MOV r0, #0
		DCW     0xE7E7
|loc_0802768C|
|unk_0802768C|
; cited by 0x080274DA (a pc-relative load targets 0x08027694)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		DCW     0xE7E4
	INCBIN  baserom.gba_0x27692_0x2769e.extracted
|sub_0802769E|
	DCW      0x0874
	DCW      0x2fdc
	DCW      0x0871
	DCW      0x8090
	DCW      0x086b
