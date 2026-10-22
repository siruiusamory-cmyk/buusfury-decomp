	CODE16
|loc_0803E40C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r5, r0, #0
	ADD      r7, r2, #0
	MOV      r4, #0
|loc_0803E416|
	LSL      r0, r4, #6
	ADD      r0, r0, r5
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	BL       |loc_0803E152|
	ADD      r4, #1
	CMP      r4, #0x10
	BLT      |loc_0803E416|
	POP      {r3, r4, r5, r6, r7, pc}
