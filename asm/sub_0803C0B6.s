	CODE16
|sub_0803C0B6|
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0]
	BX       lr
|sub_0803C0C0|
|unk_0803C0C0|
	INCBIN	baserom.gba_0x3c0c0_0x3c0c2.extracted
|sub_0803C0C2|
	DCW      0x0300
