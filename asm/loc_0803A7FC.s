	CODE16
|loc_0803A7FC|
	PUSH     {r4}
	SUB      sp, #0x10
	STRB     r1, [r0, #0xb]
	MOV      r1, #0xff
	STRB     r1, [r0, #8]
	ADD      r1, sp, #8
|loc_0803A808|
	MOV      r2, #0
	MOV      r3, #0
	STMIA    r1!, {r2, r3}
	LDRB     r1, [r0, #0xb]
	STR      r1, [sp, #8]
	LDRB     r1, [r0, #0xb]
	STR      r1, [sp, #0xc]
	LDR      r2, [r0, #0x10]
	LDR      r3, [sp, #8]
	ADD      r1, r0, #0
	SUB      r2, r2, r3
	LDR      r3, [r0, #0x14]
	LDR      r4, [sp, #0xc]
	STR      r2, [sp]
	SUB      r3, r3, r4
	STR      r3, [sp, #4]
	STR      r2, [r0, #0x18]
	STR      r3, [r0, #0x1c]
	LDR      r2, [r0, #0x10]
	LDR      r3, [sp, #8]
	LDR      r0, [r0, #0x14]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0xc]
	ADD      r1, #0x20
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	ADD      r0, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STMIA    r1!, {r0, r2}
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r6, sp, #0x28
	ADD      r7, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDMIA    r6!, {r5, r6}
	BNE      |sub_0803A86C|
	MOV      r0, #0x83
	LSL      r0, r0, #4
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0803A86C|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
