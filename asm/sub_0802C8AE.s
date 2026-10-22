	CODE16
|sub_0802C8AE|
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_0802C8F4|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_0802C8BE|
	MOV      r0, #0
	POP      {r3, pc}
