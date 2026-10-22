	CODE16
|sub_08035B34|
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_08035B7A|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_08035B44|
	MOV      r0, #0
	POP      {r3, pc}
