	CODE16
|sub_0800FDFA|
	PUSH     {r4}
	MOV      r2, #0xff
	ADD      r2, #0xa1
	LDR      r2, [r2, r1]
	MOV      r3, #0xff
	ADD      r3, #0xa5
	LDR      r3, [r3, r1]
	SUB      sp, #0x10
	ASR      r2, r2, #8
	STR      r2, [sp]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ASR      r3, r3, #8
	STR      r3, [sp, #4]
	ADD      r2, #0x91
	LDRB     r1, [r2, #0xc]
	LDRB     r2, [r2, #0xd]
	LDR      r3, [sp]
	MOV      r4, sp
	ADD      r1, r3, r1
	STR      r1, [sp, #8]
	LDR      r1, [sp, #4]
	ADD      r1, r1, r2
	STR      r1, [sp, #0xc]
	LDMIA    r4!, {r1, r2, r3, r4}
	STMIA    r0!, {r1, r2, r3, r4}
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
|loc_0800FE34|
	PUSH     {r4, r5}
	LDR      r4, [r1, #0x54]
	MOV      r2, #0xff
	MOV      r3, #4
	LDRSB    r5, [r4, r3]
	ADD      r2, #0xa1
	LDR      r2, [r2, r1]
	MOV      r3, #0xff
	ADD      r3, #0xa5
	LDR      r3, [r3, r1]
	ASR      r2, r2, #8
	ADD      r2, r2, r5
	ASR      r5, r3, #8
	MOV      r3, #5
	LDRSB    r4, [r4, r3]
	SUB      sp, #0x10
	STR      r2, [sp]
	ADD      r3, r5, r4
	STR      r3, [sp, #4]
	LDR      r2, [r1, #0x54]
	MOV      r4, sp
	LDRB     r1, [r2, #6]
	LDRB     r2, [r2, #7]
	LDR      r3, [sp]
	ADD      r1, r3, r1
	STR      r1, [sp, #8]
	LDR      r1, [sp, #4]
	ADD      r1, r1, r2
	STR      r1, [sp, #0xc]
	LDMIA    r4!, {r1, r2, r3, r4}
	STMIA    r0!, {r1, r2, r3, r4}
	ADD      sp, #0x10
	POP      {r4, r5}
	BX       lr
