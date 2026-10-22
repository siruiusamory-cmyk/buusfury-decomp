	CODE16
|sub_080029C2|
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x220]
	LDR      r0, [r0, #0x14]
	BL       |loc_08004468|
	POP      {r3, pc}
|sub_080029D8|
|unk_080029D8|
	INCBIN	baserom.gba_0x29d8_0x2a12.extracted
