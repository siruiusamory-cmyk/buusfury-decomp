	CODE16
|sub_0803F5D0|
	CMP      r0, #0
	BEQ      |loc_0803F6BA|
	CMP      r1, #0xff
	BCC      |sub_0803F5EC|
	LDR      r0, [r2, #8]
	LDR      r5, [r2, #4]
	SUB      r1, #0xff
	SUB      r1, #1
	ADD      r2, r5, #0
	MUL      r2, r1
	LSL      r1, r2, #1
	ADD      r0, r0, r1
	STR      r0, [sp, #0x130]
	B        |loc_0803F5FC|
