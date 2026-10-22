	CODE16
|sub_0800DD10|
	PUSH     {r4, lr}
	MOV      r2, #0x80
	LDR      r4, [r2, r0]
	BL       |loc_0800D72E|
	ADD      r0, r4, #0
	ADD      r0, #0x10
	LDR      r1, [r4, #0x10]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r4, pc}
	LSL      r0, r0, #0
	STMIA    r5!, {r3}
	LSR      r4, r0, #0x20
