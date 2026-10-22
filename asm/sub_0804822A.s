	CODE16
|sub_0804822A|
	LSL      r0, r0, #0xc
	ADR      r0, |loc_080484E0|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048238|
|unk_08048238|
	INCBIN	baserom.gba_0x48238_0x4823a.extracted
