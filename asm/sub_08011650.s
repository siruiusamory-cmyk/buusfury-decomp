	CODE16
|sub_08011650|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x9dc0
	CMP      r0, #0
	BEQ      |loc_0801166A|
|loc_0801165C|
	SUB      r4, #4
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x9dc0
	CMP      r0, #0
	BNE      |loc_0801165C|
|loc_0801166A|
	ADD      r5, #4
	CMP      r5, r4
	BCS      |loc_0801168A|
	ADD      r1, r5, #0
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x9dc0
	CMP      r0, #0
	BNE      |loc_0801166A|
	ADD      r0, r4, #0
	LDR      r2, [r0]
	LDR      r1, [r5]
	STR      r2, [r5]
	STR      r1, [r0]
	SUB      r4, #4
	B        |sub_08011650|
|loc_0801168A|
	LDR      r1, [r4]
	LDR      r0, [r6]
	STR      r1, [r6]
	STR      r0, [r4]
	SUB      r1, r4, #4
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0xa084
	ADD      r1, r7, #0
	ADD      r0, r4, #4
	BL       |inc_0x049120_0x055620| + 0xa084
|loc_080116A2|
	LDR      r4, [pc, #0x168]
	LDR      r0, [r4]
	BL       |inc_0x03d784_0x041118| + 0x2d0
	LDR      r0, [r4]
	MOV      r1, #0
	STR      r0, [sp]
	LDR      r0, [r4]
	MOV      r4, #0
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0xc]
	STR      r1, [sp, #8]
	CMP      r0, #0
	BLE      |loc_080116F6|
	MOV      r0, #0x41
	LDR      r1, [sp, #0x210]
	LSL      r0, r0, #3
	ADD      r6, r1, r0
	ADD      r7, sp, #0xc
|loc_080116C8|
	LSL      r0, r4, #2
	ADD      r5, r0, r7
	ADD      r5, #4
	LDR      r0, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r2, r2, r1
	MOV      r1, sp
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_080116EE|
	LDR      r0, [r6]
	LDR      r1, [r5]
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r6
	STR      r2, [r6]
	STR      r1, [r0, #4]
|loc_080116EE|
	LDR      r0, [sp, #0xc]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_080116C8|
|loc_080116F6|
	ADD      sp, #0x1fc
	ADD      sp, #0x18
	POP      {r4, r5, r6, r7, pc}
