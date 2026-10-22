	CODE16
|sub_08048402|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804840C|
|unk_0804840C|
	INCBIN	baserom.gba_0x4840c_0x4840e.extracted
