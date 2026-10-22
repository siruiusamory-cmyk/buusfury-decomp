	CODE16
|sub_0800E672|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |loc_0800E1D0|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800E15C|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |loc_0800E3E6|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800E15C|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |sub_0800E4C4|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_0800E15C|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	BEQ      |loc_0800E704|
	LSR      r7, r6, #1
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	ADD      r5, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800E6D6|
	MOV      r0, #0x89
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800E6D6|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
