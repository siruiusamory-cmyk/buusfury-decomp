	CODE16
|sub_08005E3A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x150]
	ADD      r5, r0, #0
	LDR      r1, [r1]
	ADD      r5, #0xff
	LDRH     r1, [r1, #4]
	ADD      r5, #0x2d
	ADD      r4, r5, #0
	MOV      r6, #0
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1f
	MVN      r6, r6
	SUB      r4, #0x2c
	MOV      r7, #0
	CMP      r1, #0
	BEQ      |loc_08005E72|
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	ADD      r0, r0, r5
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_08005E72|
	BL       |sub_08004C8C|
	CMP      r0, #0
	BEQ      |loc_08005E72|
	STR      r6, [r4, #0x1c]
	STR      r7, [r4, #0x10]
|loc_08005E72|
	LDR      r0, [pc, #0x11c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_08005E96|
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	ADD      r0, r0, r5
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_08005E96|
	BL       |sub_08004CE0|
	CMP      r0, #0
	BEQ      |loc_08005E96|
	STR      r6, [r4, #0x1c]
	STR      r7, [r4, #0x10]
|loc_08005E96|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	ADD      r2, r0, #0
	ADD      r2, #0xff
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r2, #0x2d
	ADD      r5, r2, #0
	SUB      r5, #0x2c
	LDR      r7, [r5, #0xc]
	SUB      sp, #0xc
	LSL      r1, r7, #7
	LDR      r3, [r2, r1]
	CMP      r3, #0
	BEQ      |loc_08005F82|
	ADD      r3, r1, r2
	ADD      r1, r3, #0
	LDR      r2, [r3, #0xc]
	ADD      r1, #0xc
	MOV      r4, #0
	CMP      r2, #0
	BLE      |loc_08005F82|
	LDR      r6, [r3, #0x7c]
	LSL      r3, r4, #1
	ADD      r3, r3, r4
	LSL      r3, r3, #2
	ADD      r3, r3, r1
	LDR      r3, [r3, #0xc]
	CMP      r3, r6
	BNE      |sub_08005F86|
	LDR      r1, [r5, #0x28]
	SUB      r1, r7, r1
	LSL      r1, r1, #5
	ADD      r0, r1, r0
	LSL      r1, r4, #2
	ADD      r0, r0, r1
	MOV      r1, #5
	LSL      r1, r1, #7
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x38]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LSL      r0, r4, #4
	ADD      r0, #0x12
	STR      r0, [sp, #4]
	LDR      r0, [r5, #0xc]
	LDR      r1, [r5, #0x28]
	MOV      r3, #0x34
	SUB      r0, r0, r1
	MUL      r0, r3
	ADD      r0, #0x2c
	STR      r0, [sp, #8]
	MOV      r6, #0
|loc_08005F06|
	LSL      r0, r6, #1
	LDR      r1, [pc, #0x84]
	ADD      r0, r0, r6
	LSL      r0, r0, #2
	ADD      r1, #0x20
	ADD      r7, r0, r1
	MOV      r0, #0x2c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08005F72|
	LDRB     r5, [r7, #2]
	LDRB     r0, [r7, #3]
	MUL      r5, r0
	LDR      r0, [pc, #0x78]
	ADD      r1, r5, #0
	STR      r0, [r4]
	LDR      r0, [pc, #0x64]
	STRH     r5, [r4, #0xe]
	LDR      r0, [r0, #0x1c]
	BL       |loc_0801124C|
	ADD      r3, r0, #1
	BNE      |loc_08005F4A|
	LDR      r0, [pc, #0x58]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |sub_08011732|
	LDR      r0, [pc, #0x4c]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |loc_0801124C|
|loc_08005F4A|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x50]
	ADD      r2, sp, #4
	STR      r0, [r4]
	STR      r7, [r4, #0x28]
	LDMIA    r2!, {r1, r2}
	STR      r1, [r4, #0x20]
	STR      r2, [r4, #0x24]
	MOV      r0, #0x3a
	STRB     r0, [r4, #8]
	LDRB     r2, [r7, #2]
	LDRB     r0, [r7, #3]
	LDR      r3, [pc, #0x40]
	MUL      r2, r0
	LDRH     r0, [r4, #0xc]
	LDR      r1, [r7, #8]
	LSL      r0, r0, #5
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08005F72|
	LDR      r0, [pc, #0x1c]
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |List_Append|
	ADD      r6, #1
	CMP      r6, #4
	BLT      |loc_08005F06|
|loc_08005F82|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
