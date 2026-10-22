	CODE16
|sub_0804888E|
	LSL      r0, r0, #0xc
	STMIA    r6!, {r4, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804889C|
|unk_0804889C|
	INCBIN	baserom.gba_0x4889c_0x4889e.extracted
