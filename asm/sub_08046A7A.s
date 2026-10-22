	CODE16
|sub_08046A7A|
	LSL      r0, r0, #0
	DCW      0xf996,0x0000
	STR      r2, [r1, r0]
	LSL      r0, r0, #0
	LSL      r6, r5, #7
	LDR      r1, [sp, #0x198]
	STR      r2, [r0, r0]
	LSL      r0, r0, #0
	LSL      r6, r5, #7
	LSL      r0, r0, #0
	STR      r3, [r0, r0]
	LSL      r0, r0, #0
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	STR      r3, [r1, r0]
	LSL      r0, r0, #0
	STR      r3, [r0, r2]
	LSL      r0, r0, #0
