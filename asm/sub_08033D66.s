	CODE16
|sub_08033D66|
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	STR      r3, [sp, #0x1f0]
	LSR      r5, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r2, #0x10
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0]
	BX       lr
|sub_08033D80|
|unk_08033D80|
	INCBIN	baserom.gba_0x33d80_0x33d82.extracted
