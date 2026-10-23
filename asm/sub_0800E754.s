	CODE16
|sub_0800E754|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, sp, #0x28
	ADD      r5, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDMIA    r7!, {r6, r7}
	BNE      |sub_0800E776|
	MOV      r0, #0x89
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800E776|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
