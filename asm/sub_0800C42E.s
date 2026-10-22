	CODE16
|sub_0800C42E|
	LSR      r3, r0, #0x20
	MOV      r4, #0xec
	LSR      r7, r0, #0x20
|loc_0800C434|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BHI      |loc_0800C538|
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	STR      r0, [r0]
	STRH     r0, [r0]
