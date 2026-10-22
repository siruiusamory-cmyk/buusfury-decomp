	CODE16
|sub_0803BABE|
	LDR      r0, [r5]
	ADD      r1, sp, #0x3c
	STR      r0, [sp, #0x3c]
	LDR      r0, [sp, #0x28]
	STR      r0, [sp, #0x40]
	LDR      r2, [r7]
	SUB      r0, r0, r2
	STR      r0, [sp, #0x20]
	BPL      |loc_0803BAD2|
|unk_0803BAD0|
	INCBIN	baserom.gba_0x3bad0_0x3bad2.extracted
