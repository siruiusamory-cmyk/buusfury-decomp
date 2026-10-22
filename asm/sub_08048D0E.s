	CODE16
|sub_08048D0E|
	LSL      r0, r0, #0xc
	POP      {r3, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D1C|
|unk_08048D1C|
	INCBIN	baserom.gba_0x48d1c_0x48d1e.extracted
