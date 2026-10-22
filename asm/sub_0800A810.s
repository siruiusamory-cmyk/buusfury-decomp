	CODE16
|sub_0800A810|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_0800A4A4|
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0x48
	LDR      r5, [r4, #4]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800A84E|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
