	CODE16
|sub_08009D24|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2e4]
	MOV      ip, r1
	ADD      r1, #4
	SUB      sp, #0x24
	STR      r0, [r4]
	MOV      r3, #0
	LDRSH    r0, [r1, r3]
	MOV      r3, #2
	MOV      lr, r1
	LDRSH    r1, [r1, r3]
	ADD      r7, r2, #0
	ADD      r2, r7, #0
	ADD      r2, #0xff
	LSL      r0, r0, #8
	LSL      r1, r1, #8
	STR      r1, [sp, #0x18]
	STR      r0, [sp, #0x14]
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	LDR      r2, [r2]
	SUB      r0, r0, r3
	SUB      r1, r1, r2
	ADD      r5, r4, #4
	ADD      r6, r5, #4
	CMP      r0, #0
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x10]
	STR      r1, [sp, #0x20]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	STR      r0, [sp, #0x1c]
	BLT      |sub_08009D6C|
	LDR      r0, [sp, #0x1c]
	B        |sub_08009D70|
