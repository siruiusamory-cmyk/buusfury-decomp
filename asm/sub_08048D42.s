	CODE16
|sub_08048D42|
	LSL      r0, r0, #0xc
	BCC      |loc_08048C88|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D50|
|unk_08048D50|
	INCBIN	baserom.gba_0x48d50_0x48d52.extracted
