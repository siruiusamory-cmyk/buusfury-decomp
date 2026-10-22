	CODE16
|sub_0800BAFE|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	STR      r0, [r3, #8]
	LDRB     r0, [r3, #2]
	LDRB     r1, [r3, #3]
	CMP      r0, r1
	BCS      |loc_0800BB12|
	LDRB     r0, [r3, #3]
	STRB     r0, [r3, #2]
|loc_0800BB12|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	LDRB     r0, [r3, #1]
	LDRB     r1, [r3, #2]
	CMP      r0, r1
	BCS      |loc_0800BB24|
	LDRB     r0, [r3, #2]
	STRB     r0, [r3, #1]
|loc_0800BB24|
	ADD      r5, r4, #0
	MOV      r6, #5
	LSL      r6, r6, #8
	ADD      r5, #0x1c
	ADD      r1, r5, #0
	ADD      r6, sp
	MOV      r2, #0xc
	ADD      r0, r6, #0
	BL       |inc_0x046118_0x049114| + 0xb3c
	CMP      r0, #0
	BEQ      |sub_0800BC20|
	LDMIA    r6!, {r0, r1, r2}
	STMIA    r5!, {r0, r1, r2}
	MOV      r3, #5
	LSL      r3, r3, #8
	MOV      r6, #1
	LSL      r6, r6, #9
	ADD      r3, sp
	LDR      r1, [r3, #8]
	ADD      r2, r6, #0
	MOV      r5, sp
	MOV      r0, sp
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r2, #3
	LSL      r2, r2, #8
	ADD      r0, r5, r6
	LDR      r1, [pc, #0x118]
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	LDRB     r0, [r3]
	CMP      r0, #0x29
	BGE      |loc_0800BB8A|
	LDR      r2, [pc, #0xdc]
	ADD      r2, #0x20
	MOV      r6, #1
|loc_0800BB74|
	LSL      r1, r0, #4
	LDR      r3, [r2, r1]
	ADD      r1, r1, r2
	STRB     r6, [r5, r3]
	LDR      r3, [r1, #4]
	ADD      r0, #1
	STRB     r6, [r5, r3]
	LDR      r1, [r1, #8]
	CMP      r0, #0x29
	STRB     r6, [r5, r1]
	BLT      |loc_0800BB74|
|loc_0800BB8A|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	LDRB     r1, [r3, #3]
	MOV      r0, #0
	CMP      r1, #0
	BLE      |loc_0800BBC0|
|loc_0800BB98|
	LDR      r3, [pc, #0xe0]
	LSL      r2, r0, #4
	LDR      r7, [r3, r2]
	LDR      r1, [pc, #0xe0]
	ADD      r2, r2, r3
	LDRB     r6, [r1, r7]
	MOV      r3, #5
	LSL      r3, r3, #8
	STRB     r6, [r5, r7]
	LDR      r6, [r2, #4]
	ADD      r3, sp
	LDRB     r7, [r1, r6]
	ADD      r0, #1
	STRB     r7, [r5, r6]
	LDR      r2, [r2, #8]
	LDRB     r1, [r1, r2]
	STRB     r1, [r5, r2]
	LDRB     r1, [r3, #3]
	CMP      r1, r0
	BGT      |loc_0800BB98|
|loc_0800BBC0|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	LDRB     r1, [r3, #2]
	CMP      r1, r0
	BLE      |loc_0800BBF4|
|loc_0800BBCC|
	LDR      r3, [pc, #0xac]
	LSL      r2, r0, #4
	LDR      r7, [r3, r2]
	LDR      r1, [pc, #0xb0]
	ADD      r2, r2, r3
	LDRB     r6, [r1, r7]
	MOV      r3, #5
	LSL      r3, r3, #8
	STRB     r6, [r5, r7]
	LDR      r6, [r2, #4]
	ADD      r3, sp
	LDRB     r7, [r1, r6]
	ADD      r0, #1
	STRB     r7, [r5, r6]
	LDR      r2, [r2, #8]
	LDRB     r1, [r1, r2]
	STRB     r1, [r5, r2]
	LDRB     r1, [r3, #2]
	CMP      r1, r0
	BGT      |loc_0800BBCC|
|loc_0800BBF4|
	MOV      r3, #5
	LSL      r3, r3, #8
	ADD      r3, sp
	LDRB     r1, [r3, #1]
	CMP      r1, r0
	BLE      |loc_0800BC02|
	LDRB     r0, [r3, #1]
|loc_0800BC02|
	CMP      r0, #0x29
	BGE      |loc_0800BC24|
	LDR      r2, [pc, #0x74]
	MOV      r6, #1
	LSL      r1, r0, #4
	LDR      r3, [r2, r1]
	ADD      r1, r1, r2
	STRB     r6, [r5, r3]
	LDR      r3, [r1, #4]
	ADD      r0, #1
	STRB     r6, [r5, r3]
	LDR      r1, [r1, #8]
	CMP      r0, #0x29
	STRB     r6, [r5, r1]
	B        |loc_0800BC22|
