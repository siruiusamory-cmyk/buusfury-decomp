	CODE16
|sub_0803F70C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	MOV      r7, #1
	ADD      r4, r0, #0
	CMP      r1, #0xff
	LDR      r2, [r0, #0xc]
	SUB      sp, #0x134
	BCC      |sub_0803F728|
	LDR      r5, [pc, #0x294]
	ADD      r0, r7, #0
	CMP      r1, r5
	BCC      |sub_0803F738|
	MOV      r0, #0
	B        |sub_0803F738|
