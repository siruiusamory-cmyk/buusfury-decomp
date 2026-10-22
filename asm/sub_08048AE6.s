	CODE16
|sub_08048AE6|
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x2c0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048AF4|
|unk_08048AF4|
	INCBIN	baserom.gba_0x48af4_0x48af6.extracted
