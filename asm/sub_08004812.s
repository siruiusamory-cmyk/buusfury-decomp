	CODE16
|sub_08004812|
	LSR      r5, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	SUB      r2, #0x54
	STRH     r4, [r3, r5]
	STRB     r7, [r5, #0x15]
	STR      r2, [r6, #0x34]
	LDRB     r5, [r4, r1]
	STR      r7, [r0, #0x14]
	STR      r5, [r5, #0x54]
	STR      r4, [r0, #0x14]
	STR      r4, [r6, #0x14]
	STR      r6, [r5, #0x30]
	STRB     r0, [r6, #1]
	LSL      r0, r0, #0
	LSL      r4, r6, #0x14
	LSL      r0, r0, #0
	PUSH     {lr}
	LSR      r4, r0, #0x20
