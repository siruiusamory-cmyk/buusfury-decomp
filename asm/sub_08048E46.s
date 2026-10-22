	CODE16
|sub_08048E46|
	LSR      r4, r0, #0x20
	ADD      r4, r4, r5
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	LDR      r1, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048E54|
|unk_08048E54|
	INCBIN	baserom.gba_0x48e54_0x48e56.extracted
