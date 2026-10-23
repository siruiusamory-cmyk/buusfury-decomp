	CODE16
|sub_0801D08E|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	CMP      r3, #0xcc
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	BX       lr
|sub_0801D0A0|
|unk_0801D0A0|
	INCBIN	baserom.gba_0x1d0a0_0x1d0a6.extracted
|sub_0801D0A6|
	DCW      0x0300
