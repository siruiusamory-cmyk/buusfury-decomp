	CODE16
|sub_0803EB56|
	LDR      r2, [pc, #0x240]
	LSL      r1, r6, #2
	ADD      r2, #0xc
	LDR      r1, [r2, r1]
	STR      r1, [r5, #0x54]
	LDRB     r1, [r4, #0xa]
	ORR      r0, r1
	STRB     r0, [r4, #0xa]
	POP      {r4, r5, r6, r7, pc}
|sub_0803EB68|
|unk_0803EB68|
	INCBIN	baserom.gba_0x3eb68_0x3eb6c.extracted
