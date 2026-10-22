	CODE16
|sub_08048AC6|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x350
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048AD4|
	DCW      0x3204
	DCW      0x0300,0xb710
|loc_08048ADA|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048AE4|
|unk_08048AE4|
	INCBIN	baserom.gba_0x48ae4_0x48ae6.extracted
