	CODE16
|sub_080003C2|
	LSR      r3, r5, #1
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	SUB      r4, r5, r6
	LSL      r0, r0, #0xc
	ASR      r0, r3, #1
	LSL      r0, r0, #0xc
	ASR      r0, r6, #0x20
	LSL      r0, r0, #0xc
	ASR      r0, r4, #0x20
	LSL      r0, r0, #0xc
	LSL      r4, r6, #0x13
	LSL      r0, r0, #0
	LDR      r1, [pc, #0x278]
	LDRB     r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r1, [pc, #0x268]
	STRB     r0, [r1]
	BX       lr
|sub_080003FC|
|unk_080003FC|
	INCBIN	baserom.gba_0x3fc_0x45e.extracted
