	CODE16
|loc_08008B30|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	MOV      r6, #7
	ADD      r4, r0, #0
	LSL      r6, r6, #0x19
	LDRB     r0, [r6]
	SUB      sp, #0xdc
	LDR      r5, [sp, #0x100]
	MOV      lr, r3
	MOV      ip, r1
	ADD      r3, sp, #0xc0
	STRB     r0, [r3, #0x18]
	LDRB     r0, [r6, #1]
	STRB     r0, [r3, #0x19]
	MOV      r1, #0
	MOV      r7, #0x9c
	MOV      r0, #1
|loc_08008B50|
	LSL      r2, r1, #5
	SUB      r2, r2, r1
	LSL      r2, r2, #1
	EOR      r2, r7
	ADD      r3, sp, #0xc0
	STRB     r2, [r3, #0x14]
	MOV      r2, #0xe3
	MUL      r2, r1
	ADD      r2, #0x25
	STRB     r2, [r3, #0x15]
	LDRB     r2, [r3, #0x14]
	STRB     r2, [r6]
	LDRB     r2, [r3, #0x15]
	STRB     r2, [r6, #1]
	LDRB     r2, [r6]
	LDRB     r3, [r3, #0x14]
	CMP      r2, r3
	BNE      |loc_08008B88|
	LDRB     r2, [r6, #1]
	ADD      r3, sp, #0xc0
	LDRB     r3, [r3, #0x15]
	CMP      r2, r3
	BNE      |loc_08008B88|
	ADD      r1, #1
	CMP      r1, #2
	BLT      |loc_08008B50|
	LDR      r1, [pc, #0x184]
	STRB     r0, [r1]
|loc_08008B88|
	ADD      r3, sp, #0xc0
	LDRB     r1, [r3, #0x18]
	STRB     r1, [r6]
	LDRB     r1, [r3, #0x19]
	STRB     r1, [r6, #1]
	LDR      r1, [r4, #4]
	MOV      r7, #0
	CMP      r1, #0
	BEQ      |loc_08008B9C|
	LDR      r7, [r1, #0x34]
|loc_08008B9C|
	MOV      r1, ip
	STR      r1, [r4, #4]
	LDRB     r2, [r1, #8]
	CMP      r2, #0
	BNE      |loc_08008BA8|
	MOV      r0, #0
|loc_08008BA8|
	STR      r0, [r4, #0xc]
	ADD      r0, r1, #0
	MOV      r1, lr
	BL       |loc_080089A0|
	STRB     r0, [r4, #2]
	LDR      r6, [pc, #0x150]
	LDRB     r2, [r4, #1]
	LDRB     r1, [r4]
	LDR      r0, [r6, #8]
	BL       |loc_08004A88|
	LDRB     r1, [r4, #2]
	LDR      r0, [r4, #4]
	BL       |sub_080089CC|
	ADD      r1, r0, #0
	LDR      r2, [sp, #0xe4]
	LDR      r0, [r6, #0xc]
	ADD      r3, r5, #0
	BL       |sub_0800953E|
	LDR      r0, [r4, #4]
	MOV      r5, #0
	LDRB     r0, [r0, #7]
	CMP      r0, #0
	BLE      |loc_08008BFE|
|loc_08008BDE|
	LDR      r0, [r4, #4]
	LSL      r1, r5, #3
	LDR      r0, [r0, #0x20]
	ADD      r1, r0, r1
	MOV      r0, #0
	BL       |loc_0800C300|
	ADD      r1, r0, #0
	LDR      r0, [r6, #0x14]
	BL       |List_Append|
	LDR      r0, [r4, #4]
	ADD      r5, #1
	LDRB     r0, [r0, #7]
	CMP      r0, r5
	BGT      |loc_08008BDE|
|loc_08008BFE|
	LDR      r0, [r4, #4]
	MOV      r5, #0
	LDRB     r0, [r0, #5]
	CMP      r0, #0
	BLE      |loc_08008C2A|
|loc_08008C08|
	LDR      r0, [r4, #4]
	LSL      r1, r5, #2
	LDR      r0, [r0, #0x18]
	LDR      r6, [r0, r1]
	LDR      r0, [r6]
	BL       |loc_08004784|
	CMP      r0, #0
	BEQ      |loc_08008C20|
	ADD      r0, r6, #0
	BL       |loc_0800C7E2|
|loc_08008C20|
	LDR      r0, [r4, #4]
	ADD      r5, #1
	LDRB     r0, [r0, #5]
	CMP      r0, r5
	BGT      |loc_08008C08|
|loc_08008C2A|
	LDR      r0, [r4, #4]
	MOV      r5, #0
	LDRB     r0, [r0, #6]
	CMP      r0, #0
	BLE      |loc_08008C62|
|loc_08008C34|
	LDR      r0, [r4, #4]
	LSL      r1, r5, #2
	LDR      r0, [r0, #0x1c]
	LDR      r6, [r0, r1]
	LDR      r0, [r6]
	BL       |loc_08004784|
	CMP      r0, #0
	BEQ      |loc_08008C58|
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |loc_0800DD2C|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xb4]
	LDR      r0, [r0, #0x14]
	BL       |List_Append|
|loc_08008C58|
	LDR      r0, [r4, #4]
	ADD      r5, #1
	LDRB     r0, [r0, #6]
	CMP      r0, r5
	BGT      |loc_08008C34|
|loc_08008C62|
	MOV      r1, #1
	ADD      r0, r4, #0
	BL       |sub_08008AA0|
	LDR      r0, [r4, #4]
	BL       |loc_080089D8|
	ADD      r1, r0, #0
	CMP      r0, #0xff
	BNE      |loc_08008C80|
	LDR      r6, [pc, #0x90]
	MOV      r1, #0
	LDR      r0, [r6]
	STRB     r1, [r0, #5]
	B        |loc_08008C9E|
|loc_08008C80|
	LDR      r6, [pc, #0x84]
	LSL      r3, r1, #2
	ADD      r1, r3, r1
	LDR      r2, [pc, #0x88]
	LSL      r1, r1, #2
	LDR      r0, [r6]
	ADD      r1, r1, r2
	LDRB     r2, [r0, #5]
	CMP      r2, #1
	BNE      |loc_08008C9A|
	LDR      r2, [r0, #0xc]
	CMP      r2, r1
	BEQ      |loc_08008C9E|
|loc_08008C9A|
	BL       |inc_0x03d784_0x041118| + 0x198c
|loc_08008C9E|
	LDR      r0, [r4, #4]
	MOV      r5, #0
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BLE      |loc_08008CD8|
|loc_08008CA8|
	LDR      r0, [r4, #4]
	LSL      r1, r5, #2
	LDR      r0, [r0, #0x14]
	LDR      r6, [r0, r1]
	LDR      r0, [r6, #4]
	BL       |loc_08004784|
	CMP      r0, #0
	BEQ      |loc_08008CCE|
	ADD      r1, r5, #0
	ADD      r0, r6, #0
	LDR      r2, [r6]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x40]
	LDR      r0, [r0, #0x14]
	BL       |List_Append|
|loc_08008CCE|
	LDR      r0, [r4, #4]
	ADD      r5, #1
	LDRB     r0, [r0, #4]
	CMP      r0, r5
	BGT      |loc_08008CA8|
|loc_08008CD8|
	CMP      r7, #0
	BEQ      |loc_08008CEC|
	MOV      r1, #0
	STR      r1, [sp, #4]
	STR      r1, [sp, #0x48]
	MOV      r2, #0
	ADD      r1, r7, #0
	ADD      r0, sp, #4
	BL       |loc_08004038|
|loc_08008CEC|
	LDR      r0, [r4, #4]
	LDR      r1, [r0, #0x30]
	CMP      r1, #0
	BEQ      |loc_08008D02|
	MOV      r0, #0
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x48]
	ADD      r0, sp, #4
	MOV      r2, #0
	BL       |loc_08004038|
|loc_08008D02|
	ADD      sp, #0xec
	POP      {r4, r5, r6, r7, pc}
|loc_08008D06|
	DCW      0x0000
	DCW      0x16a0,0x0807,0x1004,0x0300,0xb78c
|loc_08008D12|
	LSR      r3, r7, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LSL      r0, r1, #0x18
	LSR      r0, r0, #0x18
	LSL      r1, r2, #0x18
	ADD      r7, r3, #0
	LDR      r5, [sp, #0x1c]
	LDR      r6, [sp, #0x18]
	STRB     r0, [r4]
	LSR      r1, r1, #0x18
	STRB     r1, [r4, #1]
	BL       |sub_080089FC|
	ADD      r1, r0, #0
	ADD      r3, r6, #0
	ADD      r2, r7, #0
	ADD      r0, r4, #0
	STR      r5, [sp]
	BL       |loc_08008B30|
	LDR      r0, [r4, #0x10]
	ADD      r0, #1
	STR      r0, [r4, #0x10]
	POP      {r3, r4, r5, r6, r7, pc}
