	CODE16
|sub_08021068|
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08021078|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021082|
|loc_08021078|
	MOV      r1, #0
	STR      r1, [r0]
	STR      r1, [r0, #0xc]
	LDR      r1, [pc, #0x98]
	STR      r1, [r0, #8]
|loc_08021082|
	POP      {r3, pc}
	ADD      r1, r0, #0
	LDR      r1, [r1, #8]
	LDR      r2, [pc, #0x8c]
	MOV      r0, #1
	CMP      r1, r2
	BNE      |loc_08021092|
	MOV      r0, #0
|loc_08021092|
	BX       lr
|loc_08021094|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	ADD      r5, r1, #0
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r5, [r4, #8]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
|loc_080210B6|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x50]
	STR      r0, [r4, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r4, pc}
	PUSH     {r4}
	LDR      r2, [r0, #0xc]
	ADD      r1, r0, #0
	ADD      r3, r2, #1
	LSL      r2, r2, #2
	ADD      r1, #0xc
	LDR      r4, [r0, #8]
	STR      r3, [r0, #0xc]
	ADD      r1, r2, r1
	STR      r4, [r1, #4]
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0, #8]
	POP      {r4}
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4, #0xc]
	ADD      r0, r4, #0
	SUB      r1, #1
	STR      r1, [r4, #0xc]
	LSL      r1, r1, #2
	ADD      r0, #0xc
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	STR      r0, [r4, #8]
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r4, r5
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x48]
	LDR      r1, [r4, #4]
	ADD      r1, #0x80
	LDR      r1, [r1, #0x10]
	LDR      r5, [r0, #0xc]
	CMP      r1, #0
	BEQ      |sub_0802114C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08021142|
	LDR      r1, [pc, #0x34]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #8]
|loc_08021142|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |loc_08021094|
	POP      {r3, r4, r5, pc}
