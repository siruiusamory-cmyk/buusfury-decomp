	CODE16
|sub_08052EC6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
|sub_08052ECE|
|unk_08052ECE|
	INCBIN	baserom.gba_0x52ece_0x52ed2.extracted
