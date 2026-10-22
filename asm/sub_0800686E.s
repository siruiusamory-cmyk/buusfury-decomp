	CODE16
|sub_0800686E|
	LSR      r4, r0, #0x20
	STR      r1, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	LSL      r0, r3, #5
	LSR      r7, r0, #0x20
	DCW      0xf5a5,0x0803
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
