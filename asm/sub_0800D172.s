	CODE16
|sub_0800D172|
|unk_0800D172|
		MOV r2, #0
		ADD r0, r4, #0
		LDR r1, [r5, #0x28]
		BL       |loc_0800CEF4|
		LDR r0, [pc, #0x38]
		STR r0, [r4]
		STR r5, [r4, #0x34]
		LDR r0, [r5, #0x2c]
|loc_0800D184|
|unk_0800D184|
; cited by 0x0800CF08 (a pc-relative load targets 0x0800D19C)
		LDR r1, [r0, #4]
		LDR r0, [pc, #0x1c]
		LDR r0, [r0]
		BL       |loc_0801124C|
		STRH r0, [r4, #0x16]
		ADD r0, r4, #0
		BL       |sub_0800D026|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xd018
	DCB	0x00,0x00
	DCD	0x0804E454
	DCD	0x0804CDAC
		DCD     0x08072580
	INCBIN  baserom.gba_0xd1a8_0xd1b2.extracted
|sub_0800D1B2|
	DCW      0x0000
|unk_0800D1B4|
	INCBIN	baserom.gba_0xd1b4_0xd1b6.extracted
	DCW      0x0804
	DCW      0xd1e4
	DCW      0x0804
