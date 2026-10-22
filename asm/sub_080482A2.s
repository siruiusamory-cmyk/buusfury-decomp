	CODE16
|sub_080482A2|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080482AC|
|unk_080482AC|
	INCBIN	baserom.gba_0x482ac_0x482ae.extracted
