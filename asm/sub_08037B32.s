	CODE16
|sub_08037B32|
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
|unk_08037B40|
	INCBIN	baserom.gba_0x37b40_0x37b42.extracted
|dat_08037B42|
	DCW      0x0876
	DCW      0x3288
	DCW      0x0300