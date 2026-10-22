	CODE16
|sub_0803ECC6|
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r4, r5, lr}
	LDRB     r2, [r1, #0xd]
	LDR      r4, [pc, #0xe0]
	LDR      r3, [r0, #0x40]
	LSL      r2, r2, #1
	LDRH     r2, [r4, r2]
	MOV      r5, #2
	MUL      r3, r2
	LSR      r4, r3, #0xe
	STR      r4, [r0, #0x40]
	STR      r4, [r0, #0x30]
	LDRB     r2, [r0, #0x10]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDR      r3, [r0, #0x44]
	CMP      r4, r3
	BCS      |loc_0803ED06|
	STR      r3, [r0, #0x40]
	STR      r3, [r0, #0x30]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDRB     r2, [r1, #0xa]
	MOV      r3, #8
	BIC      r2, r3
	STRB     r2, [r1, #0xa]
	LDR      r1, [pc, #0x9c]
	STR      r1, [r0, #0x54]
	BL       |loc_0803E5DA|
	POP      {r4, r5, pc}
|loc_0803ED06|
	LDRB     r3, [r1, #8]
	LDRB     r4, [r1, #0xb]
	ADD      r3, r3, r4
	LSL      r3, r3, #0x18
	ASR      r3, r3, #0x18
	STRB     r3, [r1, #8]
	CMP      r3, #0x40
	BLT      |loc_0803ED1E|
	MOV      r3, #0x40
	STRB     r3, [r1, #8]
	LDR      r3, [pc, #0x98]
	STR      r3, [r0, #0x54]
|loc_0803ED1E|
	LDRB     r1, [r1, #8]
	STRB     r1, [r0, #0x12]
	MOV      r1, #0x10
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	POP      {r4, r5, pc}
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r4, r5, lr}
	LDRB     r2, [r1, #0xd]
	LDR      r4, [pc, #0x84]
	LDR      r3, [r0, #0x40]
	LSL      r2, r2, #1
	LDRH     r2, [r4, r2]
	MOV      r5, #2
	MUL      r3, r2
	LSR      r4, r3, #0x10
	STR      r4, [r0, #0x40]
	STR      r4, [r0, #0x30]
	LDRB     r2, [r0, #0x10]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDR      r3, [r0, #0x44]
	CMP      r4, r3
	BCS      |loc_0803ED6A|
	STR      r3, [r0, #0x40]
	STR      r3, [r0, #0x30]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDRB     r2, [r1, #0xa]
	MOV      r3, #8
	BIC      r2, r3
	STRB     r2, [r1, #0xa]
	LDR      r1, [pc, #0x38]
	STR      r1, [r0, #0x54]
	BL       |loc_0803E5DA|
	POP      {r4, r5, pc}
|loc_0803ED6A|
	LDRB     r3, [r1, #8]
	LDRB     r4, [r1, #0xb]
	ADD      r3, r3, r4
	LSL      r3, r3, #0x18
	ASR      r3, r3, #0x18
	STRB     r3, [r1, #8]
	CMP      r3, #0x40
	BLT      |loc_0803ED82|
	MOV      r3, #0x40
	STRB     r3, [r1, #8]
	LDR      r3, [pc, #0x34]
	STR      r3, [r0, #0x54]
|loc_0803ED82|
	LDRB     r1, [r1, #8]
	STRB     r1, [r0, #0x12]
	MOV      r1, #0x10
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	POP      {r4, r5, pc}
|loc_0803ED8E|
	DCW      0x0000
	DCW      0x6724,0x087b,0xe5ad,0x0803,0x6ec4,0x087b,0xe5db,0x0803
	DCW      0xeb99,0x0803,0xebf9,0x0803,0x9c40,0x0000,0xe8bd,0x0803
	DCW      0x6a04,0x087b,0xe7c5
|loc_0803EDB6|
	LSR      r3, r0, #0x20
	LDR      r4, [r0, #0x48]
	LSR      r3, r7, #1
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r4, r5, lr}
	LDRB     r2, [r1, #0xd]
	LDR      r4, [pc, #0x27c]
	LDR      r3, [r0, #0x40]
	LSL      r2, r2, #1
	LDRH     r2, [r4, r2]
	MOV      r5, #2
	MUL      r3, r2
	LSR      r4, r3, #0xe
	STR      r4, [r0, #0x40]
	STR      r4, [r0, #0x30]
	LDRB     r2, [r0, #0x10]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDR      r3, [r0, #0x44]
	CMP      r4, r3
	BLS      |loc_0803EDFC|
	STR      r3, [r0, #0x40]
	STR      r3, [r0, #0x30]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDRB     r2, [r1, #0xa]
	MOV      r3, #8
	BIC      r2, r3
	STRB     r2, [r1, #0xa]
	LDR      r1, [pc, #0x254]
	STR      r1, [r0, #0x54]
	BL       |loc_0803E5AC|
	POP      {r4, r5, pc}
|loc_0803EDFC|
	LDRB     r3, [r1, #8]
	LDRB     r4, [r1, #0xb]
	SUB      r3, r3, r4
	LSL      r3, r3, #0x18
	ASR      r3, r3, #0x18
	STRB     r3, [r1, #8]
	CMP      r3, #0
	BGT      |loc_0803EE14|
	MOV      r3, #0
	STRB     r3, [r1, #8]
	LDR      r3, [pc, #0x238]
	STR      r3, [r0, #0x54]
|loc_0803EE14|
	LDRB     r1, [r1, #8]
	STRB     r1, [r0, #0x12]
	MOV      r1, #0x10
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	POP      {r4, r5, pc}
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r4, r5, lr}
	LDRB     r2, [r1, #0xd]
	LDR      r4, [pc, #0x224]
	LDR      r3, [r0, #0x40]
	LSL      r2, r2, #1
	LDRH     r2, [r4, r2]
	MOV      r5, #2
	MUL      r3, r2
	LSR      r4, r3, #0x10
	STR      r4, [r0, #0x40]
	STR      r4, [r0, #0x30]
	LDRB     r2, [r0, #0x10]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDR      r3, [r0, #0x44]
	CMP      r4, r3
	BCS      |loc_0803EE60|
	STR      r3, [r0, #0x40]
	STR      r3, [r0, #0x30]
	ORR      r2, r5
	STRB     r2, [r0, #0x10]
	LDRB     r2, [r1, #0xa]
	MOV      r3, #8
	BIC      r2, r3
	STRB     r2, [r1, #0xa]
	LDR      r1, [pc, #0x1f0]
	STR      r1, [r0, #0x54]
	BL       |loc_0803E5AC|
	POP      {r4, r5, pc}
|loc_0803EE60|
	LDRB     r3, [r1, #8]
	LDRB     r4, [r1, #0xb]
	SUB      r3, r3, r4
	LSL      r3, r3, #0x18
	ASR      r3, r3, #0x18
	STRB     r3, [r1, #8]
	CMP      r3, #0
	BGT      |loc_0803EE78|
	MOV      r3, #0
	STRB     r3, [r1, #8]
	LDR      r3, [pc, #0x1d4]
	STR      r3, [r0, #0x54]
|loc_0803EE78|
	LDRB     r1, [r1, #8]
	STRB     r1, [r0, #0x12]
	MOV      r1, #0x10
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	POP      {r4, r5, pc}
