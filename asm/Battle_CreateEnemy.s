	CODE16
|Battle_CreateEnemy|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x14
	BNE      |sub_0800F6AE|
	MOV      r0, #0xa7
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800F6AE|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
