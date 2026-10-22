	CODE16
|sub_080199F6|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	CMP      r1, #0
	SUB      sp, #8
	BEQ      |sub_08019A12|
	MOV      r0, #1
	CMP      r1, #0x1d
	BEQ      |loc_08019ACE|
	CMP      r1, #0x1e
	BNE      |loc_08019AD8|
	ADD      r4, #0x5c
	STMIA    r4!, {r0, r2}
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
