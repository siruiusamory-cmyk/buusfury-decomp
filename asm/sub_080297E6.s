	CODE16
|sub_080297E6|
	MOV      r5, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080297F8|
	LDR      r1, [pc, #0x64]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
|loc_080297F8|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	STR      r0, [r6, #4]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [sp, #4]
	STR      r7, [sp]
	CMP      r0, #0
	BEQ      |loc_08029820|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08029820|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	LDR      r2, [r0, #4]
	LDR      r1, [r1, #0x14]
	MOV      r3, #1
	ADD      r0, r3, #0
	CMP      r1, r2
	BEQ      |loc_08029832|
	MOV      r0, #0
|loc_08029832|
	SUB      r0, r3, r0
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029846|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
|loc_08029846|
	POP      {r3, pc}
	LSL      r4, r3, #8
	LSR      r5, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	ADD      r7, pc, #0x160
	LSR      r4, r0, #0x20
	STR      r7, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	LDR      r3, [pc, #0xfc]
	ADD      r2, r4, #0
	LDR      r3, [r3]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	ADD      r3, #0xff
	ADD      r3, #0xa1
	LDMIA    r2!, {r5}
	LDMIA    r3!, {r6}
	LDR      r2, [r2]
	LDR      r3, [r3]
	SUB      sp, #0x10
	SUB      r2, r2, r3
	STR      r2, [sp, #4]
	LDR      r3, [sp, #4]
	SUB      r5, r5, r6
	ADD      r1, r0, #0
	ADD      r1, #8
	STR      r5, [sp]
	STR      r5, [sp, #8]
	STR      r3, [sp, #0xc]
	STMIA    r1!, {r5}
	LDR      r2, [sp, #0xc]
	STR      r2, [r1]
	ADD      r1, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xdd08
	MOV      r0, #0x37
	STRB     r0, [r4, #8]
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4}
	LDR      r2, [pc, #0xbc]
	ADD      r0, #8
	LDR      r2, [r2]
	LDMIA    r0!, {r4}
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	LDR      r2, [r2]
	LDR      r0, [r0]
	SUB      sp, #0x10
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	ADD      r3, r3, r4
	LDR      r2, [sp, #4]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	STR      r3, [sp]
	STR      r3, [sp, #8]
	STR      r2, [sp, #0xc]
	STR      r3, [r1]
	ADD      r0, r1, #4
	LDR      r1, [sp, #0xc]
	STR      r1, [r0]
	ADD      sp, #0x10
	POP      {r4}
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080298EE|
	MOV      r1, #3
	STRB     r1, [r0, #4]
	LDR      r1, [pc, #0x7c]
	STR      r1, [r0]
|loc_080298EE|
	ADD      r5, r0, #0
	MOV      r1, #1
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0x64]
	MOV      r5, #0
	LDR      r0, [r0]
	SUB      sp, #0x1c
	CMP      r0, #0
	BEQ      |loc_0802991A|
	MOV      r1, #0xff
	ADD      r1, #0xcd
	LDR      r1, [r1, r0]
	CMP      r1, #0
	BNE      |sub_08029920|
|loc_0802991A|
	MOV      r0, #1
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
