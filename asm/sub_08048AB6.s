	CODE16
|sub_08048AB6|
	LSL      r0, r0, #0xc
|unk_08048AB8|
	INCBIN	baserom.gba_0x48ab8_0x48aba.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048AC0|
	STR      r0, [r1]
	BX       lr
|sub_08048AC4|
|unk_08048AC4|
	INCBIN	baserom.gba_0x48ac4_0x48ac6.extracted
