	CODE16
|sub_08041068|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x9c]
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |sub_08041078|
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
