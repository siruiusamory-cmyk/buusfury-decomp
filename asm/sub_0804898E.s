	CODE16
|sub_0804898E|
	LSR      r4, r0, #0x20
	ADD      r1, #8
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048B98|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080489A0|
|unk_080489A0|
	INCBIN	baserom.gba_0x489a0_0x489a2.extracted
