	CODE16
|sub_0801785C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r0, #1
	LSL      r1, r0, #8
	STR      r0, [r4, #4]
	LDR      r0, [r4, #8]
	BL       |inc_0x046118_0x049114| + 0xd40
	MOV      r1, #0xff
	ADD      r1, #1
	SUB      r0, r1, r0
	BL       |inc_0x0158_0x143f2| + 0x6f82
	ADD      r1, r4, #4
	LDMIA    r1!, {r0, r1}
	CMP      r0, r1
	BLT      |sub_08017884|
	MOV      r0, #1
	POP      {r4, pc}
