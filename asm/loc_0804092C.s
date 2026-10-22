	CODE16
|loc_0804092C|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xb0
	ADD      r5, r1, #0
	LSL      r0, r0, #0x10
	LSR      r1, r0, #0x10
	LSL      r2, r2, #0x18
	LSR      r7, r2, #0x18
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	CMP      r1, r0
	BCC      |loc_08040950|
	LDR      r0, [pc, #4]
	B        |loc_08040A84|
|loc_08040948|
	DCW      0x52f8
	DCW      0x0300,0x80ff,0x0000
