	CODE16
|sub_080487F6|
	LSL      r0, r0, #0xc
|unk_080487F8|
	INCBIN	baserom.gba_0x487f8_0x487fa.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048804|
|unk_08048804|
	INCBIN	baserom.gba_0x48804_0x48806.extracted
