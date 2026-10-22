	CODE16
|sub_08048952|
	LSL      r0, r0, #0xc
	POP      {r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048960|
|unk_08048960|
	INCBIN	baserom.gba_0x48960_0x48962.extracted
