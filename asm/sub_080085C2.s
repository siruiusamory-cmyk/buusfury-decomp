	CODE16
|sub_080085C2|
	MOV      r1, #0
	MVN      r1, r1
	ADD      r3, sp, #0x3fc
	LDR      r0, [r3, #0x34]
	LDR      r0, [r0]
	LDR      r3, [r4, #4]
	ADD      r0, r0, r1
	BPL      |sub_080085D8|
	LDRB     r3, [r3, #4]
	ADD      r0, r0, r3
	B        |loc_080085E0|
