	CODE16
|loc_08040A8C|
	PUSH     {r4, r5, lr}
	SUB      sp, #8
	ADD      r4, r1, #0
	LSL      r0, r0, #0x10
	LSR      r1, r0, #0x10
	MOV      r5, #0
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	CMP      r1, r0
	BCC      |loc_08040AB0|
	LDR      r0, [pc, #8]
	B        |loc_08040ADA|
|loc_08040AA6|
	DCW      0x0000
	DCW      0x52f8,0x0300,0x80ff,0x0000
