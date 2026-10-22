	CODE16
|sub_080482AE|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x3a0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080482BC|
|unk_080482BC|
	INCBIN	baserom.gba_0x482bc_0x482be.extracted
