	CODE16
|sub_0803F444|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r1, #0xff
	LDR      r2, [r0, #0xc]
	SUB      sp, #0x2c
	BCC      |sub_0803F45E|
	LDR      r6, [pc, #0x2b0]
	MOV      r0, #1
	CMP      r1, r6
	BCC      |sub_0803F46E|
	MOV      r0, #0
	B        |sub_0803F46E|
