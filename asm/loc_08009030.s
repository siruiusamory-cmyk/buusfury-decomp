	CODE16
|loc_08009030|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0xdc
	ADD      r7, sp, #0x104
	LDMIA    r7!, {r6, r7}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	MOV      r5, #0
	CMP      r0, #0
	BEQ      |loc_08009044|
	LDR      r5, [r0, #0x34]
|loc_08009044|
	LDR      r0, [r4, #0x10]
	ADD      r0, #1
	STR      r0, [r4, #0x10]
	LSL      r0, r1, #0x18
	LSR      r0, r0, #0x18
	LSL      r1, r2, #0x18
	LSR      r1, r1, #0x18
	STRB     r0, [r4]
	STRB     r1, [r4, #1]
	BL       |sub_080089FC|
	STR      r0, [r4, #4]
|loc_0800905C|
	LDR      r1, [sp, #0xe8]
	BL       |loc_080089A0|
	LSL      r1, r0, #0x18
	LSR      r1, r1, #0x18
	STRB     r1, [r4, #2]
	LDR      r0, [r4, #4]
	BL       |sub_080089CC|
	ADD      r1, r0, #0
	ADD      r3, r7, #0
	LDR      r7, [pc, #0x188]
	LDR      r2, [sp, #0x100]
	LDR      r0, [r7, #0xc]
	BL       |sub_0800953E|
	MOV      r7, #0
	CMP      r5, #0
	BEQ      |loc_08009090|
	MOV      r2, #0
	ADD      r1, r5, #0
	STR      r7, [sp, #4]
	STR      r7, [sp, #0x48]
	ADD      r0, sp, #4
	BL       |loc_08004038|
|loc_08009090|
	LDR      r0, [r4, #4]
	LDR      r1, [r0, #0x30]
	CMP      r1, #0
	BEQ      |loc_080090A4|
	STR      r7, [sp, #4]
	STR      r7, [sp, #0x48]
	MOV      r2, #0
	ADD      r0, sp, #4
	BL       |loc_08004038|
|loc_080090A4|
	CMP      r6, #0
	BEQ      |loc_080090E2|
	LDR      r0, [r4, #4]
	MOV      r5, #0
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BLE      |loc_080090E2|
	LDR      r7, [pc, #0x148]
|loc_080090B4|
	LDR      r0, [r4, #4]
	LSL      r1, r5, #2
	LDR      r0, [r0, #0x14]
	LDR      r6, [r0, r1]
	LDR      r0, [r6, #4]
	BL       |loc_08004784|
	CMP      r0, #0
	BEQ      |loc_080090D8|
	ADD      r1, r5, #0
	ADD      r0, r6, #0
	LDR      r2, [r6]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
|loc_080090D8|
	LDR      r0, [r4, #4]
	ADD      r5, #1
	LDRB     r0, [r0, #4]
	CMP      r0, r5
	BGT      |loc_080090B4|
|loc_080090E2|
	ADD      sp, #0xec
	POP      {r4, r5, r6, r7, pc}
