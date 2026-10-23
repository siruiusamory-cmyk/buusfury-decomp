	CODE16
|sub_0801E12E|
|unk_0801E12E|
		CMP r1, #0
		DCW     0xD104
		LDR r1, [r0, #0x44]
		CMP r1, #0
		DCW     0xD101
		MOV r0, #0
		DCW     0xE7F7
	INCBIN  baserom.gba_0x1e13c_0x1e13e.extracted
|sub_0801E13E|
|unk_0801E13E|
	INCBIN	baserom.gba_0x1e13e_0x1e142.extracted
|dat_0801E142|
	DCW      0x0000
	DCW      0xb480
	DCW      0x0804
	DCW      0x02e8
	DCW      0x0872