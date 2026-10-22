	CODE16
|sub_0802BD36|
	LSL      r0, r0, #0
	SUB      r2, #8
	LSR      r5, r6, #1
|loc_0802BD3C|
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	BCS      |loc_0802BD3C|
	LSR      r3, r7, #0x20
