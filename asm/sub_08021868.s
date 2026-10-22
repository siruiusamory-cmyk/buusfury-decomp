	CODE16
|sub_08021868|
|unk_08021868|
		LDR r0, [r4, #0x30]
		STR r0, [r4, #4]
		MOV r0, #1
		DCW     0xE7F9
	INCBIN  baserom.gba_0x21870_0x21872.extracted
