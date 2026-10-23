	CODE16
|sub_0803934E|
	LSL      r0, r0, #0
	ADD      r6, sp, #0x160
	LSR      r7, r6, #1
	ASR      r0, r4, #0xf
	LSR      r1, r6, #1
	ADD      r2, #0xa4
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0]
	BX       lr
|sub_08039360|
|unk_08039360|
	INCBIN	baserom.gba_0x39360_0x39362.extracted
|sub_08039362|
	DCW      0x0300
