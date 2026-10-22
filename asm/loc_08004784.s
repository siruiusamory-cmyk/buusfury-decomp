	CODE16
|loc_08004784|
	PUSH     {r4, r5, lr}
	SUB      sp, #0x6c
	CMP      r0, #0
	BNE      |sub_08004792|
	MOV      r0, #1
	ADD      sp, #0x6c
	POP      {r4, r5, pc}
