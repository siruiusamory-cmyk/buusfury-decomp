	CODE16
|sub_0800EB36|
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	ADR      r7, |loc_0800EDC0|
	LSR      r4, r0, #0x20
	LSR      r5, r1, #0x13
	LSL      r0, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDRH     r2, [r1, #0x10]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STRH     r2, [r0, #0x10]
	LDRH     r2, [r1, #0x12]
	STRH     r2, [r0, #0x12]
	LDRH     r2, [r1, #0x14]
	STRH     r2, [r0, #0x14]
	LDRH     r1, [r1, #0x16]
	STRH     r1, [r0, #0x16]
	BX       lr
	LSL      r0, r0, #0
