	CODE16
|sub_0804889E|
	LSL      r0, r0, #0xc
	SUB      sp, #0x160
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080488AC|
|unk_080488AC|
	INCBIN	baserom.gba_0x488ac_0x488ae.extracted
