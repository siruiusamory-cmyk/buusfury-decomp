	CODE16
|sub_0804862E|
	LSR      r4, r0, #0x20
	CMP      r7, #0xd8
	LSL      r0, r0, #0xc
	ADR      r6, |loc_080488B8|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048640|
|unk_08048640|
	INCBIN	baserom.gba_0x48640_0x48642.extracted
