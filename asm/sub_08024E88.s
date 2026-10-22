	CODE16
|sub_08024E88|
	MOV      r0, #0xa0
	STR      r0, [r4, #4]
	MOV      r0, #0x16
	STR      r0, [r4, #8]
	ADD      r3, r2, #1
	BNE      |sub_08024E98|
	ADD      r1, pc, #0x94
	B        |loc_08024E9A|
