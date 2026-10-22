	CODE16
|sub_08003C74|
	LDR      r2, [r1]
	ADD      r3, r2, #1
	STR      r3, [r1]
	LDR      r1, [r0]
	LDRB     r3, [r2]
	ADD      r2, r1, #1
	STR      r2, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r3, [r0, #4]
	BX       lr
|sub_08003C8A|
|unk_08003C8A|
	INCBIN	baserom.gba_0x3c8a_0x3cac.extracted
