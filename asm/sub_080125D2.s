	CODE16
|sub_080125D2|
	LSR      r4, r0, #0x20
	CMP      r2, #0x58
	LSL      r0, r0, #0xc
	CMP      r0, #0xa0
	LSR      r7, r0, #0x20
	LDR      r5, [sp, #0x60]
	LSR      r4, r0, #0x20
