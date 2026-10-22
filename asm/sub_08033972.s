	CODE16
|sub_08033972|
	LSL      r0, r0, #0
	ADD      r2, #4
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BCC      |loc_08033996|
	MOV      r0, #0x10
	STRH     r0, [r1, #0x12]
|loc_08033996|
	LDRH     r0, [r1, #0x12]
	LSR      r0, r0, #3
	STRB     r0, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	SUB      sp, #0x30
	MOV      r6, #0
	STR      r6, [r0, #8]
	LDR      r0, [pc, #0x18c]
	ADD      r5, r1, #0
	LDR      r4, [r0]
	MOV      r1, #9
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	STRB     r6, [r4, #0x11]
	LDRB     r0, [r5, #0x10]
	MOV      r1, #1
	EOR      r0, r1
	STRB     r0, [r4, #0x10]
	ADD      r0, r4, #0
	LDR      r1, [pc, #0x174]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x174]
	ADD      r6, sp, #0x10
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r6!, {r1, r2, r3}
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r6!, {r1, r2, r3}
	LDMIA    r0!, {r2, r3}
	STMIA    r6!, {r2, r3}
	ADD      r1, r4, #0
	LDRB     r2, [r5, #0x10]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	SUB      r6, #0x20
	LSL      r2, r2, #3
	ADD      r2, r2, r6
	LDMIA    r1!, {r3}
	LDMIA    r2!, {r4}
	LDR      r1, [r1]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	LDR      r2, [r2]
	SUB      r3, r3, r4
	ADD      r0, #0xa1
	SUB      r1, r1, r2
	STR      r1, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r3, [sp]
	STR      r3, [sp, #8]
	STR      r2, [sp, #0xc]
	STMIA    r0!, {r3}
	LDR      r1, [sp, #0xc]
	STR      r1, [r0]
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033A14|
	LDR      r1, [pc, #0x12c]
	STR      r1, [r0]
|loc_08033A14|
	ADD      r4, r0, #0
	MOV      r1, #0x12
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      sp, #0x30
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x104]
	ADD      r6, r1, #0
	LDR      r4, [r7]
	ADD      r5, r0, #0
	CMP      r4, #0
	SUB      sp, #0x1c
	BNE      |sub_08033A40|
	MOV      r0, #1
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
