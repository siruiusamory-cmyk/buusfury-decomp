	CODE16
|sub_0801611C|
	MOV      r1, #0
	STR      r1, [r2, #8]
	LDR      r2, [r4, #0x20]
	STR      r1, [r2, #8]
	LDR      r1, [r4, #0x48]
	STR      r1, [sp, #0xc]
	LDR      r1, [r4, #0x28]
	ADD      r1, #3
	STR      r1, [sp, #0x10]
	LDR      r1, [r4, #0x30]
	SUB      r1, #3
	STR      r1, [sp, #0x18]
	LDR      r1, [r4, #0x30]
	SUB      r1, #5
	STR      r1, [sp, #8]
	LDR      r1, [r4, #0x38]
	LDR      r5, [r4, #0x34]
	CMP      r1, r5
	BLE      |loc_08016184|
	ADD      r6, r4, #0
	ADD      r6, #0x4c
|loc_08016146|
	LSL      r0, r5, #1
	ADD      r0, r0, r5
	LSL      r0, r0, #2
	ADD      r0, r0, r6
	ADD      r0, #4
	LDR      r1, [r0, #8]
	LDR      r2, [sp, #0xc]
	ADD      r1, #6
	ADD      r1, r2, r1
	STR      r1, [sp, #0x14]
	ADD      r1, r2, #3
	STR      r1, [sp, #4]
	LDR      r1, [r4, #0x40]
	MOV      r2, #1
	CMP      r1, r5
	BEQ      |loc_08016168|
	MOV      r2, #0
|loc_08016168|
	STR      r2, [sp]
	LDR      r3, [r0]
	ADD      r0, r7, #0
	ADD      r2, sp, #4
	ADD      r1, sp, #0xc
	BL       |loc_08015BB8|
	LDR      r0, [sp, #0x14]
	ADD      r5, #1
	ADD      r0, #4
	STR      r0, [sp, #0xc]
	LDR      r0, [r4, #0x38]
	CMP      r0, r5
	BGT      |loc_08016146|
|loc_08016184|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x1c]
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_08016198|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
