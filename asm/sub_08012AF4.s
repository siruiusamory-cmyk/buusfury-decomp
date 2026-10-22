	CODE16
|sub_08012AF4|
	LDR      r1, [r4]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, #0x16
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	CMP      r0, #0
	BEQ      |loc_08012B28|
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #4
	LSL      r1, r0, #0x18
	LDR      r0, [r4]
	LSR      r1, r1, #0x18
	LDR      r2, [r0, #0x28]
	ADD      r2, r2, r0
	B        |sub_08012B22|
