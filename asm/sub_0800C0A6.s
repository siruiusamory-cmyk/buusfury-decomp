	CODE16
|sub_0800C0A6|
	LSL      r0, r0, #0
	MOV      r4, #0x8c
	LSR      r7, r0, #0x20
	DCW      0xf5a5,0x0803
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	PUSH     {r3, r5, lr}
	LSR      r4, r0, #0x20
	STR      r0, [r0, #0x18]
	STRH     r0, [r0]
	MOV      r1, #0x80
	LSR      r0, r4
