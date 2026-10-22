	CODE16
|sub_08054EF8|
	LSL      r0, r1, #0
	LSL      r7, r3, #0x16
	ASR      r0, r1, #0x20
	ASR      r7, r3, #0x16
	LSL      r0, r0, #0
	ASR      r0, r4, #0xe
|unk_08054F04|
	INCBIN	baserom.gba_0x54f04_0x54f08.extracted
	LSL      r0, r0, #0
	LDRB     r0, [r0, #0x1f]
	LSL      r0, r0, #0
	LDRB     r0, [r7, #0x1f]
	BX       pc
	LSL      r0, r0, #0
