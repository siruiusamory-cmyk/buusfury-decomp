|sub_0800A7A0|
	EXPORT |sub_0800A7A0|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800A7C0|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
