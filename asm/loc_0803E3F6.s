	CODE16
|loc_0803E3F6|
	PUSH     {r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r4, #0
|loc_0803E3FC|
	LSL      r0, r4, #6
	ADD      r0, r0, r5
	BL       |loc_0803E0B6|
	ADD      r4, #1
	CMP      r4, #0x10
	BLT      |loc_0803E3FC|
	POP      {r4, r5, pc}
