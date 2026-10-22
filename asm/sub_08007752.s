	CODE16
|sub_08007752|
	LDR      r0, [pc, #0x10]
	ADD      r0, #8
	BX       lr
	LDR      r0, [pc, #8]
	ADD      r0, #0x18
	BX       lr
	LDR      r0, [pc, #4]
	ADD      r0, #0x10
	BX       lr
|sub_08007764|
|unk_08007764|
	INCBIN	baserom.gba_0x7764_0x7766.extracted
