	CODE16
|sub_08029A60|
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0xec]
	ADD      r5, r1, #0
	LDR      r4, [r0]
	SUB      sp, #0x24
	CMP      r4, #0
	BNE      |sub_08029A74|
	MOV      r0, #0
	ADD      sp, #0x24
	POP      {r4, r5, pc}
