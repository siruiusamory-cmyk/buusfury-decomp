	CODE16
|sub_0800C276|
	LSR      r4, r0, #0x20
	MOV      r4, #0xd4
	LSR      r7, r0, #0x20
	BHI      |loc_0800C210|
	LSR      r4, r0, #0x20
	DCW      0xf5a5,0x0803
	MOV      r4, #0x8c
	LSR      r7, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	STR      r0, [r0]
	STRH     r0, [r0]
	MOV      r0, #0x88
	LSR      r0, r4
