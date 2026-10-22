	CODE16
|sub_0800A64A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x4c]
	ADD      r3, r2, r1
	ADD      r1, r5, #0
	ADD      r1, #0x28
	MOV      r2, #1
	ADD      r7, r1, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x50]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	ADD      r1, #0x38
	ADD      r6, r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4]
	ADD      r5, r0, #0
	LDR      r2, [r1, #0x4c]
	ADD      r0, r4, #0
	ADD      r3, r2, r1
	ADD      r1, r6, #0
	CMP      r5, #0
	BNE      |loc_0800A688|
	ADD      r1, r7, #0
|loc_0800A688|
	MOV      r2, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	ADD      r0, r5, #0
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x4c]
	ADD      r3, r2, r1
	ADD      r1, r0, #0
	ADD      r1, #0x38
	MOV      r2, #1
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800A6D0|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800A6D0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
