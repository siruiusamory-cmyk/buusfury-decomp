	CODE16
|loc_0800A9FE|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r5, r0, #0
	BL       |List_ReleaseAll1|
	LDR      r0, [r5, #4]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0800AA3A|
	ADD      r7, r5, #4
|loc_0800AA12|
	LSL      r0, r4, #3
	ADD      r6, r0, r7
	ADD      r6, #4
	LDR      r0, [r6]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	LDR      r1, [r5]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r6]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_0800AA12|
|loc_0800AA3A|
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0800AA46|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_0800AA46|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|loc_0800AA4A|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LSL      r0, r1, #3
	LDR      r1, [pc, #0xfc]
	ADD      r7, r0, r1
	LDR      r0, [r7]
	LDR      r1, [r4]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4, #4]
	ADD      r6, r0, #0
	ADD      r0, r4, #4
	LSL      r1, r1, #3
	ADD      r5, r1, r0
	SUB      r5, #4
	LDR      r0, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4, #0x30]
	ADD      r0, r4, #0
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r0, #0x30
	LDR      r3, [r5]
	STR      r2, [r4, #0x30]
	ADD      r0, r1, r0
	STR      r3, [r0, #4]
	STMIA    r5!, {r6, r7}
	LDR      r1, [r6]
	ADD      r0, r6, #0
	LDR      r2, [r1]
	ADD      r2, r2, r1
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, r4, r5, r6, r7, pc}
|loc_0800AA9C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	CMP      r0, #5
	BGE      |loc_0800AAD6|
	LSL      r0, r1, #3
	LDR      r1, [pc, #0xa4]
	ADD      r5, r0, r1
	LDR      r0, [r5]
	LDR      r1, [r4]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r2, [r4, #4]
	ADD      r1, r0, #0
	ADD      r3, r2, #1
	LSL      r2, r2, #3
	ADD      r0, r4, #4
	ADD      r0, r2, r0
	ADD      r0, #4
	STR      r3, [r4, #4]
	STMIA    r0!, {r1, r5}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800AAD6|
	POP      {r3, r4, r5, pc}
|loc_0800AAD8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r0, #4
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #3
	ADD      r5, r1, r0
	ADD      r5, #4
	LDR      r0, [r5]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4, #0x30]
	ADD      r0, r4, #0
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r0, #0x30
	LDR      r3, [r5]
	STR      r2, [r4, #0x30]
	ADD      r0, r1, r0
	STR      r3, [r0, #4]
	POP      {r3, r4, r5, pc}
