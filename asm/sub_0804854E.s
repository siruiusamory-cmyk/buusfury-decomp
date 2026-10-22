	CODE16
|sub_0804854E|
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x1e0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804855C|
|unk_0804855C|
	INCBIN	baserom.gba_0x4855c_0x4855e.extracted
