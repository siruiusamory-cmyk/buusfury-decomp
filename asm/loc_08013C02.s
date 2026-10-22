	CODE16
|loc_08013C02|
	PUSH     {r4, r5, lr}
	LDR      r2, [pc, #0x21c]
	MOV      r3, #0x16
	LDRSB    r5, [r1, r3]
	LDR      r4, [r2, #0x14]
	SUB      sp, #0x6c
	ADD      r3, r4, r5
	STR      r3, [r2, #0x14]
	MOV      r3, #0x17
	LDRSB    r5, [r1, r3]
	LDR      r4, [r2, #0x18]
	ADD      r3, r4, r5
	STR      r3, [r2, #0x18]
	MOV      r3, #0x18
	LDRSB    r5, [r1, r3]
	LDR      r4, [r2, #0x1c]
	ADD      r3, r4, r5
	STR      r3, [r2, #0x1c]
	MOV      r3, #0x19
	LDRSB    r5, [r1, r3]
	LDR      r4, [r2, #0x20]
	ADD      r3, r4, r5
	STR      r3, [r2, #0x20]
	MOV      r3, #0x1a
	LDRSB    r5, [r1, r3]
	LDR      r4, [r2, #0x24]
	ADD      r3, r4, r5
	STR      r3, [r2, #0x24]
	LDRH     r3, [r2, #4]
	LDR      r4, [r1, #0x1c]
	ADD      r3, r3, r4
	STRH     r3, [r2, #4]
	LDR      r2, [r1, #0x28]
	CMP      r2, #0
	BEQ      |loc_08013C62|
	MOV      r3, #0x24
	LDRB     r3, [r3, r1]
	LDRB     r2, [r0, #0x13]
	ORR      r2, r3
	STRB     r2, [r0, #0x13]
	MOV      r0, #0
	LDR      r1, [r1, #0x28]
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	MOV      r2, #0
	BL       |loc_08004038|
|loc_08013C62|
	ADD      sp, #0x6c
	POP      {r4, r5, pc}
