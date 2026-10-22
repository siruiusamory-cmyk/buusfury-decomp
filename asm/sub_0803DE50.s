	CODE16
|sub_0803DE50|
	PUSH     {lr}
	LDR      r2, [r0, #4]
	SUB      sp, #0xc
	STR      r2, [sp, #4]
	LDR      r2, [r0, #8]
	SUB      r2, #0xc
	STR      r2, [sp, #8]
	LDR      r3, [r0, #0x20]
	ADD      r2, sp, #4
	BL       |inc_0x046118_0x049114| + 0x98e
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {r4, r5, r6, r7}
	LDRH     r4, [r1]
	CMP      r4, #0
	BNE      |sub_0803DE78|
	MOV      r4, #1
	STR      r4, [r3, #0xc]
	B        |sub_0803DE88|
