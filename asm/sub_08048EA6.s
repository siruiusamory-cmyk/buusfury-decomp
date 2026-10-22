	CODE16
|sub_08048EA6|
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #8]
	LDR      r1, [pc, #0xc]
	STR      r0, [r1]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048EB4|
|unk_08048EB4|
	INCBIN	baserom.gba_0x48eb4_0x48eb6.extracted
