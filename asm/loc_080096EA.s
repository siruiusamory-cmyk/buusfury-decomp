	CODE16
|loc_080096EA|
	PUSH     {r4, r5}
	MOV      r3, #1
	ADD      r0, #0xa0
	LSL      r3, r1
	LSL      r4, r2, #0x1f
	CMP      r4, #0
	LDRH     r5, [r0, #4]
	BGE      |sub_08009700|
	ORR      r3, r5
	STRH     r3, [r0, #4]
	B        |sub_08009704|
