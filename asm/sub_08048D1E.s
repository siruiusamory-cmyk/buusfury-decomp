	CODE16
|sub_08048D1E|
	LSL      r0, r0, #0xc
	SWI      0x74
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D2C|
|unk_08048D2C|
	INCBIN	baserom.gba_0x48d2c_0x48d2e.extracted
