	CODE16
|sub_08007398|
|unk_08007398|
; cited by 0x08007324 (a pc-relative load targets 0x080073B8)
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #0x14]
		STR r0, [r4]
		LDR r0, [r5, #0x10]
		STR r0, [r4, #0x10]
		MOV r0, #0
		STR r0, [r4, #0x14]
		STR r0, [r4, #0x18]
		STR r0, [r4, #0x1c]
		STR r0, [r4, #0x20]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x723e
	INCBIN  baserom.gba_0x73b6_0x73b8.extracted
		DCD     0x08049784
	INCBIN  baserom.gba_0x73bc_0x73be.extracted
|sub_080073BE|
	DCW      0x0804
