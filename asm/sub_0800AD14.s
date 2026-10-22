	CODE16
|sub_0800AD14|
	PUSH     {r3, lr}
	CMP      r1, #0xa
	BEQ      |sub_0800AD2C|
	CMP      r1, #0xc
	BNE      |loc_0800AD3A|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	POP      {r3, pc}
