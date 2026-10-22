	CODE16
|sub_08013E22|
	LSR      r3, r5, #1
	CMP      r3, #0x5c
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	STRB     r0, [r0, #2]
	LSR      r3, r5, #1
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	SUB      r3, #0xac
	LSR      r1, r0, #0x20
