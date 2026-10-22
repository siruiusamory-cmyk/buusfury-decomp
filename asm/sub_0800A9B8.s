	CODE16
|sub_0800A9B8|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r3, [r1, #0x74]
	ADD      r3, r3, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
	LSL      r0, r0, #0
	SUB      r4, r6, r3
	LSL      r0, r0, #0xc
