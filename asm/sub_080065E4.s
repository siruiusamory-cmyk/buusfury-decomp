	CODE16
|sub_080065E4|
	PUSH     {r3, lr}
	ADD      r3, r1, #0
	ADD      r1, r2, #0
	CMP      r3, #0
	LDR      r0, [pc, #0x24]
	BEQ      |sub_080065FE|
	CMP      r3, #1
	BEQ      |loc_08006606|
	CMP      r3, #2
	BNE      |loc_080065FC|
	LDR      r0, [r0, #8]
	STRB     r1, [r0]
|loc_080065FC|
	POP      {r3, pc}
