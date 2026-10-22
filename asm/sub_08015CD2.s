	CODE16
|sub_08015CD2|
	LDR      r2, [r0, #4]
	ADD      r2, #0xff
	ADD      r2, #1
	LDR      r2, [r2, #0xc]
	LDR      r3, [r0, #8]
	CMP      r2, r3
	BEQ      |loc_08015CE4|
	MOV      r0, #0
	BX       lr
|loc_08015CE4|
	LDR      r2, [r0, #0x30]
	STR      r2, [r1]
	LDR      r0, [r0, #0x34]
	SUB      r0, #3
	STR      r0, [r1, #4]
	MOV      r0, #1
	BX       lr
	PUSH     {r4, lr}
	LDR      r2, [r0, #0x38]
	SUB      sp, #8
	STR      r2, [sp]
	ADD      r4, r1, #0
	ADD      r1, r0, #0
	ADD      r2, r0, #0
	ADD      r2, #0x30
	ADD      r1, #0x20
	LDR      r3, [r0, #0x1c]
	ADD      r0, r4, #0
	BL       |loc_08015BB8|
	ADD      sp, #8
	POP      {r4, pc}
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x14
	LDR      r5, [sp, #0x40]
	LDR      r6, [sp, #0x3c]
	LDR      r7, [sp, #0x38]
	ADD      r4, r0, #0
	BNE      |sub_08015D30|
	MOV      r0, #0xff
	ADD      r0, #0x15
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08015D30|
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
