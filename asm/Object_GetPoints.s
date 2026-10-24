	CODE16
|Object_GetPoints|
	PUSH     {r4, r5}
	LDRB     r3, [r1, #0x10]
	ADD      r2, r0, #0
	LDR      r0, [r1, #0x58]
	LSL      r3, r3, #4
	ADD      r0, r0, r3
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r3}
	LDR      r1, [r1]
	SUB      sp, #0x20
	ASR      r3, r3, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #0x14]
	ADD      r1, r3, #0
	STR      r3, [sp, #0x10]
	LDR      r3, [sp, #0x14]
	STR      r1, [sp, #0x18]
	ADD      r0, #0x10
	STR      r3, [sp, #0x1c]
	LDR      r1, [r0]
	LDR      r3, [sp, #0x18]
	ADD      r1, r1, r3
	LDR      r3, [r0, #4]
	LDR      r4, [sp, #0x1c]
	STR      r1, [sp]
	ADD      r3, r3, r4
	STR      r3, [sp, #4]
	LDR      r4, [sp, #4]
	ADD      r3, r1, #0
	ADD      r0, #8
	LDR      r1, [r0]
	LDR      r5, [sp, #0x18]
	LDR      r0, [r0, #4]
	ADD      r1, r1, r5
	LDR      r5, [sp, #0x1c]
	STR      r1, [sp]
	ADD      r0, r0, r5
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r3, [sp, #8]
	ADD      r3, sp, #8
	STR      r0, [sp, #0x10]
	LDR      r1, [sp, #4]
	ADD      r0, r3, #0
	STR      r4, [sp, #0xc]
	ADD      r4, r2, #0
	STR      r1, [sp, #0x14]
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r4!, {r0, r1, r2, r3}
	ADD      sp, #0x20
	POP      {r4, r5}
	BX       lr
