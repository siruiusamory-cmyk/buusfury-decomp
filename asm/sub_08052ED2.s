	CODE16
|sub_08052ED2|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
|sub_08052EDA|
|unk_08052EDA|
	INCBIN	baserom.gba_0x52eda_0x52ede.extracted
