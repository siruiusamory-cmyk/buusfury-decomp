	CODE16
|sub_08013D0E|
	ADD      r0, r5, #0
	LDR      r1, [r4, #0x18]
	ADD      r0, #0x4e
	CMP      r1, #0
	BGE      |sub_08013D22|
|loc_08013D18|
	STRH     r7, [r0]
	LDRH     r1, [r0]
	CMP      r1, r7
	BNE      |loc_08013D18|
	B        |loc_08013D2E|
