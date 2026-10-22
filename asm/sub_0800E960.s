	CODE16
|sub_0800E960|
	MOV      r3, #0
	MOV      r2, #3
	BL       |sub_0800AD3E|
	STR      r0, [r4, #0x18]
|loc_0800E96A|
	MOV      r0, #0
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #0x58]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
