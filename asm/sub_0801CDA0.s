	CODE16
|sub_0801CDA0|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801CDB4|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0801CDB4|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x390]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x228]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x44
	CMP      r1, #0
	BNE      |sub_0801CDD6|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
