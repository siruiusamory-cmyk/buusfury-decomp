	CODE16
|sub_0800AD3E|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x38]
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r7, r3, #0
	SUB      sp, #4
	LDR      r0, [r4]
	BL       |loc_080116FC|
	MOV      r1, #0xff
	ADD      r1, #1
	CMP      r0, r1
	BGE      |sub_0800AD5E|
	MOV      r0, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
