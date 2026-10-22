	CODE16
|Math_Divide1|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x320]
	ADD      r4, r0, #0
	LDR      r0, [r5, #0xc]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDR      r1, [r4, #0x2c]
	CMP      r1, #0
	BNE      |loc_0800B970|
	LDR      r1, [r0, #8]
	CMP      r1, #0
	BLT      |loc_0800B970|
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x30c]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1f
	BEQ      |loc_0800B970|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |sub_0800B5F0|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x2c]
	LDR      r0, [r5, #8]
	BL       |List_Append|
|loc_0800B970|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x1f
	BEQ      |loc_0800B994|
	LDR      r0, [r5, #0xc]
	BL       |loc_080043C2|
	CMP      r0, #0
	BEQ      |loc_0800B994|
	LDR      r0, [r5, #4]
	LDR      r5, [pc, #0x2dc]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x2d0]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0800B994|
	ADD      r0, r4, #0
	BL       |loc_0800B8FC|
	POP      {r3, r4, r5, pc}
