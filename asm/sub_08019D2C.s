	CODE16
|sub_08019D2C|
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_08019D3A|
	MOV      r0, #0
	POP      {r3, pc}
