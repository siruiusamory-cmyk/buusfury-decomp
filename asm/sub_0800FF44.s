	CODE16
|sub_0800FF44|
	PUSH     {r4, r5, lr}
	ADD      r5, r0, #0
	SUB      sp, #0x20
	ADD      r0, sp, #0x10
	ADD      r4, r1, #0
	BL       |Object_GetPoints|
	LDR      r0, [sp, #0x10]
	LDR      r1, [sp, #0x18]
	LDR      r2, [sp, #0x1c]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x14]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp]
	STR      r1, [sp, #8]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	LDRB     r2, [r4, #0x10]
	CMP      r2, #0
	BEQ      |sub_0800FF8A|
	CMP      r2, #1
	BEQ      |loc_0800FF96|
	CMP      r2, #2
	BEQ      |loc_0800FF9C|
	CMP      r2, #3
	BNE      |loc_0800FF84|
	LDR      r0, [sp, #0x18]
	LDR      r1, [sp, #0xc]
|loc_0800FF84|
	STMIA    r5!, {r0, r1}
	ADD      sp, #0x20
	POP      {r4, r5, pc}
