	CODE16
|loc_08013C66|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r0, #0x28
	LDRB     r0, [r0]
	LDR      r4, [pc, #0x1b4]
	STR      r0, [r4, #0x14]
	ADD      r0, r5, #0
	ADD      r0, #0x29
	LDRB     r0, [r0]
	STR      r0, [r4, #0x18]
	ADD      r0, r5, #0
	ADD      r0, #0x2a
	LDRB     r1, [r0]
	STR      r1, [r4, #0x1c]
	LDRB     r0, [r0]
	STR      r0, [r4, #0x20]
	ADD      r0, r5, #0
	ADD      r0, #0x2b
	LDRB     r0, [r0]
	STR      r0, [r4, #0x24]
	MOV      r0, #0xff
	ADD      r0, #1
	STRH     r0, [r4, #4]
	STRH     r0, [r4, #6]
	MOV      r0, #0
	STRH     r0, [r4, #8]
	MOV      r0, #0xff
	ADD      r0, #1
	STRH     r0, [r4, #0xa]
	LSL      r0, r0, #4
	STRH     r0, [r4, #0xc]
	MOV      r0, #0x10
	STRB     r0, [r4, #1]
	STRB     r0, [r4, #2]
	LSL      r0, r0, #0xa
	STRH     r0, [r4, #0xe]
	MOV      r0, #0
	STRH     r0, [r4, #0x10]
	ADD      r1, r4, #0
	ADD      r1, #0x28
	STRB     r0, [r4]
	STR      r1, [sp]
|loc_08013CBA|
	STRB     r0, [r1]
	LDRB     r2, [r1]
	CMP      r2, r0
	BNE      |loc_08013CBA|
	ADD      r7, r0, #0
	MOV      r6, #0
	STRB     r0, [r5, #0x13]
|loc_08013CC8|
	LSL      r0, r6, #2
	ADD      r0, r0, r5
	ADD      r0, #0x3c
	LDR      r0, [r0]
	MOV      r3, #0x2c
	LDR      r1, [pc, #0x154]
	MUL      r0, r3
	ADD      r1, r0, r1
	ADD      r0, r5, #0
	BL       |loc_08013C02|
	ADD      r6, #1
	CMP      r6, #4
	BLT      |loc_08013CC8|
	LDR      r0, [pc, #0x144]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |loc_080046AE|
	ADD      r0, r5, #0
	LDR      r1, [r4, #0x14]
	ADD      r0, #0x4c
	CMP      r1, #0
	BGE      |sub_08013D02|
|loc_08013CF8|
	STRH     r7, [r0]
	LDRH     r1, [r0]
	CMP      r1, r7
	BNE      |loc_08013CF8|
	B        |sub_08013D0E|
