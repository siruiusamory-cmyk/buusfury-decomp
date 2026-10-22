	CODE16
|sub_0804859E|
	LSR      r4, r0, #0x20
	CMP      r5, #0x98
	LSL      r0, r0, #0xc
	STR      r3, [sp, #0x70]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080485B0|
|unk_080485B0|
	INCBIN	baserom.gba_0x485b0_0x485b2.extracted
