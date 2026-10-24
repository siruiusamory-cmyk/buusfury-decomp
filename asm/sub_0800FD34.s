	CODE16
|sub_0800FD34|
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r2, [r0, #8]
	LSL      r3, r2, #3
	SUB      r2, r3, r2
	LDR      r3, [pc, #0x10]
	LSL      r2, r2, #2
	ADD      r2, r2, r3
	ADD      r3, r1, #0
	ADD      r1, r0, #0
	MOV      r0, #0
	BL       |Battle_CreateEnemy|
	POP      {r3, pc}
	LSL      r0, r0, #0
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r2, #0
	ADD      r5, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_0800FD96|
	MOV      r0, #0xff
	ADD      r0, #0xb1
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800FD96|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
