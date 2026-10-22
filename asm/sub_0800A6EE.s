	CODE16
|sub_0800A6EE|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r5, #0x38]
	LDR      r2, [r5, #0x48]
	CMP      r2, r1
	BGT      |loc_0800A714|
	LDR      r1, [r5, #0x4c]
	LDR      r2, [r5, #0x3c]
	CMP      r1, r2
	BGT      |loc_0800A714|
	LDR      r1, [r5, #0x50]
	LDR      r2, [r5, #0x40]
	CMP      r1, r2
	BLT      |loc_0800A714|
	LDR      r1, [r5, #0x54]
	LDR      r2, [r5, #0x44]
	CMP      r1, r2
	BGE      |sub_0800A718|
|loc_0800A714|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
