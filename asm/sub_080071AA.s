	CODE16
|sub_080071AA|
	LDR      r0, [pc, #0x14]
	ADD      r0, #8
	BX       lr
	LDR      r0, [pc, #0xc]
	ADD      r0, #0x10
	BX       lr
	LDR      r0, [pc, #8]
	ADD      r0, #0x18
	BX       lr
|sub_080071BC|
|unk_080071BC|
	INCBIN	baserom.gba_0x71bc_0x71be.extracted
|sub_080071BE|
	DCW      0x0807
	DCW      0x1918
	DCW      0x0300
