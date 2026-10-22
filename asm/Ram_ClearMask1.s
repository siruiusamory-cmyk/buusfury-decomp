	CODE16
|Ram_ClearMask1|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	BL       |inc_0x049120_0x055620| + 0xa0
	LSL      r1, r0, #0x18
	MOV      r0, #0
	LDR      r6, [pc, #0x134]
	LSR      r1, r1, #0x18
	CMP      r1, #0
	STRB     r0, [r6, #3]
	BEQ      |loc_08040DB2|
	MOV      r4, #0
|loc_08040D66|
	LSL      r1, r4, #1
	ADD      r1, r1, r4
	LSL      r1, r1, #2
	LSR      r1, r1, #1
	LDR      r0, [r6, #0x2c]
	LSL      r1, r1, #1
	ADD      r5, r0, r1
	MOV      r1, #0
	MOV      r0, #0
|loc_08040D78|
	LSL      r2, r0, #1
	LDRH     r2, [r5, r2]
	ADD      r0, #1
	ADD      r1, r2, r1
	CMP      r0, #4
	BCC      |loc_08040D78|
	LSL      r0, r1, #0x10
	ASR      r0, r0, #0x10
	ADD      r3, r0, #7
	BNE      |loc_08040DA0|
	LSL      r0, r4, #2
	ADD      r1, r0, r7
	ADD      r0, r5, #4
	LDR      r2, [pc, #0x12c]
	SWI      0xb
	LDRB     r0, [r6, #3]
	MOV      r1, #1
	LSL      r1, r4
	ORR      r0, r1
	STRB     r0, [r6, #3]
|loc_08040DA0|
	MOV      r0, #0
	STR      r0, [sp]
	LDR      r2, [pc, #0x11c]
	ADD      r1, r5, #4
	MOV      r0, sp
	SWI      0xb
	ADD      r4, #1
	CMP      r4, #2
	BLT      |loc_08040D66|
|loc_08040DB2|
	LDRB     r1, [r6, #2]
	LDRB     r0, [r6, #3]
	ORR      r1, r0
	STRB     r1, [r6, #2]
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [pc, #0xe4]
	SUB      sp, #8
	LDR      r2, [r1]
	LDR      r4, [pc, #0xc8]
	STR      r2, [sp, #4]
	LDRB     r2, [r4, #1]
	MOV      r5, #1
	CMP      r2, #0
	BEQ      |Irq_WriteEnableAndTimer3|
	CMP      r2, #1
	BEQ      |loc_08040E28|
	CMP      r2, #2
	BNE      |loc_08040E42|
	B        |loc_08040E3E|
