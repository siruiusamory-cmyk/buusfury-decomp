	CODE16
|sub_0804FDA2|
	LSL      r0, r0, #0
	LDR      r0, [pc, #8]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1f
	BX       lr
|sub_0804FDB0|
|unk_0804FDB0|
	INCBIN	baserom.gba_0x4fdb0_0x4fdb2.extracted
