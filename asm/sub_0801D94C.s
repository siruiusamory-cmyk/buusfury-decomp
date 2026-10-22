	CODE16
|sub_0801D94C|
|unk_0801D94C|
		MOV r0, #0
		STR r0, [r5, #4]
		STR r0, [r5, #8]
		LDR r1, [r5]
		STR r0, [r1, #8]
		DCW     0xE7F7
	INCBIN  baserom.gba_0x1d958_0x1d95a.extracted
