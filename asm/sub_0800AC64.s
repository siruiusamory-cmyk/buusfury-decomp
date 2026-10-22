	CODE16
|sub_0800AC64|
	ADD      r0, #0x20
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	SUB      sp, #0x18
	ASR      r1, r1, #3
	ASR      r0, r0, #3
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r0, [sp, #8]
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	ADD      r0, #0x20
	STR      r0, [sp, #0x10]
	ADD      r0, r1, #0
	ADD      r0, #8
	STR      r0, [sp, #0x14]
	LDR      r0, [pc, #0xf4]
	STR      r1, [sp, #0xc]
	LDR      r0, [r0, #0xc]
	ADD      r0, #0x18
	LDR      r1, [r0]
	LDR      r2, [sp, #0x10]
	CMP      r1, r2
	BGE      |sub_0800ACB2|
	LDR      r1, [sp, #8]
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |sub_0800ACB2|
	LDR      r1, [r0, #4]
	LDR      r2, [sp, #0x14]
	CMP      r1, r2
	BGE      |sub_0800ACB2|
	LDR      r1, [sp, #0xc]
	LDR      r0, [r0, #0xc]
	CMP      r1, r0
	BGE      |sub_0800ACB2|
	MOV      r0, #1
	ADD      sp, #0x18
	BX       lr
