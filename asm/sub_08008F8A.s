	CODE16
|sub_08008F8A|
	ADD      r7, r5, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08008F9C|
	LDR      r1, [pc, #0x8c]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
|loc_08008F9C|
	LDR      r7, [pc, #0x78]
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ca2
	ADD      r1, r6, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
	ADD      r1, r5, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
	LDR      r0, [r7, #8]
	LDRB     r0, [r0, #1]
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |loc_08008FCE|
	MOV      r0, #0
	BL       |loc_0800B854|
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
|loc_08008FCE|
	LDR      r0, [r4, #4]
	BL       |sub_08008A36|
	LDRH     r1, [r4, #8]
	CMP      r1, r0
	BEQ      |loc_08008FF0|
	STRH     r0, [r4, #8]
	CMP      r0, #0
	BEQ      |loc_08008FF0|
	ADD      r1, r0, #0
	MOV      r0, #0
	BL       |loc_0800BF34|
	ADD      r1, r0, #0
	LDR      r0, [r7, #0x14]
	BL       |List_Append|
|loc_08008FF0|
	LDR      r0, [r7, #4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_0800900E|
	LDR      r0, [sp, #0x30]
	STR      r6, [r0]
	LDR      r0, [sp, #0x34]
	STR      r5, [r0]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
