	CODE16
|sub_0800D010|
	CMP      r6, #8
	BNE      |loc_0800D022|
	LDRH     r0, [r4, #0x14]
	CMP      r0, r5
	BNE      |sub_0800D01E|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
