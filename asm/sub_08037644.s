	CODE16
|sub_08037644|
|unk_08037644|
		ADD r1, r6, #0
		ADD r1, #0x24
		ADD r0, r5, #0
	INCBIN  baserom.gba_0x3764a_0x3764c.extracted
|sub_0803764C|
|unk_0803764C|
	INCBIN	baserom.gba_0x3764c_0x37650.extracted
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0x40
	SUB      sp, #0x54
	STR      r0, [sp, #0x50]
	LDRB     r0, [r0]
	ADD      r6, r4, #0
	ADD      r6, #0x28
	CMP      r0, #0
	LDR      r7, [pc, #0x21c]
	BEQ      |sub_08037682|
	CMP      r0, #1
	BEQ      |loc_080376CE|
	CMP      r0, #2
	BNE      |loc_0803774E|
	LDR      r0, [r4, #0x5c]
	SUB      r0, #1
	STR      r0, [r4, #0x5c]
	BNE      |loc_08037750|
	ADD      r1, r4, #0
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x5c
	POP      {r4, r5, r6, r7, pc}
