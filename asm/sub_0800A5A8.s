	CODE16
|sub_0800A5A8|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	LDR      r1, [pc, #0x1dc]
	ADD      r4, r0, #0
	LDR      r1, [r1]
	ADD      r4, #0x38
	ADD      r5, r1, #0
	ADD      r5, #0x80
	MOV      r2, #1
	ADD      r0, r4, #0
	LDR      r1, [r5, #0x28]
	SUB      sp, #0x10
	BL       |loc_08009930|
	MOV      r2, #1
	ADD      r0, r4, #0
	LDR      r1, [r5, #0x30]
	BL       |loc_08009930|
	ADD      r1, r6, #0
	MOV      r0, sp
	BL       |Object_WriteBounds1|
	MOV      r2, #0
	MOV      r0, sp
	LDR      r1, [r5, #0x28]
	BL       |loc_08009930|
	MOV      r2, #0
	MOV      r0, sp
	LDR      r1, [r5, #0x30]
	BL       |loc_08009930|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800A606|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800A606|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
