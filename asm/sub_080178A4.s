	CODE16
|sub_080178A4|
	LSL      r1, r1, #8
	BL       |inc_0x046118_0x049114| + 0xd40
	BL       |inc_0x0158_0x143f2| + 0x6f82
	ADD      r1, r4, #4
	LDMIA    r1!, {r0, r1}
	LSL      r1, r1, #1
	CMP      r0, r1
	BLT      |sub_080178BC|
	MOV      r0, #1
	POP      {r4, pc}
