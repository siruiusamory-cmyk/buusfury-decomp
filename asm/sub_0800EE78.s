	CODE16
|sub_0800EE78|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x358]
	SUB      r0, #4
	STR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
|loc_0800EE9E|
	ADD      r1, r0, #0
	LDR      r2, [pc, #0x340]
	LDR      r1, [r1, #0x14]
	MOV      r0, #1
	SUB      r2, #4
	CMP      r1, r2
	BEQ      |loc_0800EEAE|
	MOV      r0, #0
|loc_0800EEAE|
	BX       lr
