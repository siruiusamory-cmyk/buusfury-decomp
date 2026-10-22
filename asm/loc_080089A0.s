	CODE16
|loc_080089A0|
	PUSH     {lr}
	SUB      sp, #0x6c
	CMP      r1, #0
	BEQ      |sub_080089AE|
	ADD      r0, r1, #0
	ADD      sp, #0x6c
	POP      {pc}
