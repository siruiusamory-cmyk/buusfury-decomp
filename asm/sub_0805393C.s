	CODE16
|sub_0805393C|
	LSL      r3, r0, #0xf
	DCW      0xea00,0x0000,0xffe0,0x0011
	ASR      r0, r0, #0x20
	LSL      r1, r2, #0
	LSL      r0, r0, #0x10
	LSL      r2, r2, #0
	LSL      r0, r0, #0x10
	BX       pc
	LSL      r0, r0, #0
