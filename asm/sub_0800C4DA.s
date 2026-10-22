	CODE16
|sub_0800C4DA|
	PUSH     {r4, r5}
	LDR      r1, [r0, #0x1c]
	LDR      r2, [pc, #0xbc]
	ASR      r3, r1, #8
	LDR      r1, [r0, #0x20]
	SUB      sp, #8
	ASR      r1, r1, #8
	STR      r1, [r0, #4]
	SUB      r2, #8
	LDR      r2, [r2, #4]
	ADD      r4, r0, #0
	ADD      r2, #0x28
	LDR      r5, [r2]
	LDR      r2, [r2, #4]
	SUB      r3, r3, r5
	SUB      r1, r1, r2
	STR      r1, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r3, [sp]
	ADD      r4, #0x2c
	STR      r2, [r4, #4]
	LDR      r2, [pc, #0x94]
	STR      r3, [r4]
	LDR      r1, [r0, #0x2c]
	ADD      r2, #0x40
	LDR      r3, [r2]
	CMP      r1, r3
	BLT      |sub_0800C52E|
	LDR      r3, [r2, #8]
	CMP      r1, r3
	BGE      |sub_0800C52E|
	LDR      r0, [r0, #0x30]
	LDR      r1, [r2, #4]
	CMP      r0, r1
	BLT      |sub_0800C52E|
	LDR      r1, [r2, #0xc]
	CMP      r0, r1
	BGE      |sub_0800C52E|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
