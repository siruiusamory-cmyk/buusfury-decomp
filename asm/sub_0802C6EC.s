	CODE16
|sub_0802C6EC|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	SUB      sp, #0x34
	CMP      r0, #0
	BEQ      |sub_0802C6FE|
	MOV      r0, #1
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
