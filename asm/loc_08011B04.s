	CODE16
|loc_08011B04|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [r0, #4]
	ADD      r1, r0, #4
	SUB      sp, #0xc
	ADD      r4, r0, #0
	SUB      r5, #1
	CMP      r5, #0
	STR      r1, [sp, #8]
	BLT      |loc_08011B2C|
|loc_08011B16|
	LDR      r1, [sp, #8]
	LSL      r0, r5, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r5, #1
	BPL      |loc_08011B16|
|loc_08011B2C|
	LDR      r0, [pc, #0x274]
	ADD      r5, r4, r0
	LDR      r6, [r5]
	SUB      r6, #1
	BMI      |loc_08011B4A|
|loc_08011B36|
	LSL      r0, r6, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r6, #1
	BPL      |loc_08011B36|
|loc_08011B4A|
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r6, r4, r0
	LDR      r7, [r6]
	SUB      r7, #1
	BMI      |loc_08011B6A|
|loc_08011B56|
	LSL      r0, r7, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r7, #1
	BPL      |loc_08011B56|
|loc_08011B6A|
	LDR      r1, [sp, #8]
	MOV      r7, #0
	ADD      r0, r1, #4
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x230]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x41
	LSL      r0, r0, #3
	ADD      r0, r4, r0
	STR      r0, [sp, #4]
	ADD      r0, #4
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x21c]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r0, r5, #4
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x210]
	BL       |inc_0x049120_0x055620| + 0xc
	ADD      r0, r6, #4
	MOV      r2, #0x80
	LDR      r1, [pc, #0x20c]
	BL       |inc_0x049120_0x055620| + 0xc
	STR      r7, [r4, #4]
	LDR      r0, [sp, #4]
	LDR      r2, [pc, #0x204]
	STR      r7, [r0]
	ADD      r0, r2, #0
	ADD      r0, #0xff
	ADD      r0, #0x31
	STR      r7, [r5]
	MVN      r1, r7
	ADD      r0, r4, r0
	STR      r7, [r6]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x69
	LSL      r2, r2, #4
	ADD      r0, r4, r2
	STRB     r7, [r0, #4]
	ADD      r0, r2, #0
	SUB      r0, #0x10
	ADD      r0, r4, r0
	MOV      r1, #1
	LSL      r1, r1, #9
	STRH     r7, [r0, #0x16]
	STRH     r1, [r0, #0x18]
	MOV      r0, #1
|loc_08011BD6|
	LSL      r3, r0, #2
	ADD      r3, r3, r0
	LSL      r3, r3, #1
	ADD      r3, r3, r4
	ADD      r1, r0, #1
	ADD      r3, r3, r2
	STRB     r1, [r3, #0xa]
	ADD      r0, #0xff
	STRB     r0, [r3, #0xb]
	ADD      r0, r1, #0
	CMP      r1, #0x8a
	BLT      |loc_08011BD6|
	MOV      r1, #0x35
	LSL      r1, r1, #5
	ADD      r1, r4, r1
	MOV      r0, #0xff
	STRB     r0, [r1, #5]
	MOV      r1, #0xbf
	LSL      r1, r1, #4
	ADD      r1, r4, r1
	STRB     r0, [r1, #4]
	MOV      r0, #0
	STRB     r0, [r4]
	MOV      r0, #1
	STRB     r0, [r4, #1]
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
