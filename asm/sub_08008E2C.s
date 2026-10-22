	CODE16
|sub_08008E2C|
	LDR      r0, [r4, #4]
	BL       |sub_08008A36|
	LDR      r1, [sp, #0x10]
	ADD      r6, r0, #0
	LDR      r0, [r1, #0x10]
	CMP      r0, #0
	BEQ      |loc_08008E4E|
	MOV      r0, #0
	BL       |loc_0800C0C8|
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
	STRH     r6, [r4, #8]
	B        |loc_08008E6A|
|loc_08008E4E|
	LDRH     r0, [r4, #8]
	CMP      r0, r6
	BEQ      |loc_08008E6A|
	STRH     r6, [r4, #8]
	CMP      r6, #0
	BEQ      |loc_08008E6A|
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |loc_0800BF34|
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
|loc_08008E6A|
	ADD      r0, r5, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	MOV      r3, #0
	ADD      r4, r0, #0
	LDRSH    r0, [r1, r3]
	SUB      sp, #0xc
	LDR      r7, [sp, #0x3c]
	SUB      r0, #0x70
	STR      r0, [sp, #4]
	MOV      r3, #2
	LDRSH    r0, [r1, r3]
	MOV      r6, #0
	ADD      r5, r1, #0
	SUB      r0, #0x4c
	STR      r0, [sp, #8]
	MOV      r1, #0x5a
	STRB     r6, [r4]
	STRB     r1, [r4, #1]
	ADD      r0, r6, #0
	BL       |sub_080089FC|
	MOV      r2, #1
	STR      r2, [sp]
	ADD      r1, r0, #0
	ADD      r3, r6, #0
	ADD      r0, r4, #0
	ADD      r2, sp, #4
	BL       |loc_08008B30|
	LDR      r0, [r4, #0x10]
	ADD      r3, sp, #0
	ADD      r0, #1
	STR      r0, [r4, #0x10]
	MOV      r0, #0x31
	MVN      r0, r0
	STRH     r0, [r3]
	STRH     r6, [r3, #2]
	LDRH     r0, [r5]
	SUB      r0, #0x32
	STRH     r0, [r3]
	LDRH     r0, [r5, #2]
	STRH     r0, [r3, #2]
	LDR      r0, [pc, #0x154]
	LDR      r0, [r0, #4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_08008EF4|
	MOV      r0, #0x55
	LSL      r0, r0, #3
	BL       |GBARam_Malloc|
	ADD      r6, r0, #0
	BEQ      |sub_08008F10|
	MOV      r2, sp
	ADD      r0, r6, #0
	LDR      r1, [sp, #0x14]
	LDR      r3, [sp, #0x38]
	BL       |sub_08010A3A|
	LDR      r0, [pc, #0x138]
	STR      r0, [r6]
	B        |sub_08008F10|
