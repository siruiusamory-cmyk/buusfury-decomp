	CODE16
|sub_08029526|
	PUSH     {r3, lr}
	CMP      r1, #0
	BNE      |loc_0802957E|
	LDR      r1, [r0, #0x4c]
	CMP      r1, #0
	BNE      |loc_0802957A|
	LDR      r1, [r2, #0x30]
	CMP      r1, r0
	BNE      |sub_0802953C|
	MOV      r0, #0
	POP      {r3, pc}
