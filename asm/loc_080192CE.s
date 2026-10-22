	CODE16
|loc_080192CE|
	PUSH     {r4, r5, r6, lr}
	SUB      sp, #0x10
	ADD      r5, r2, #0
	MOV      r2, #1
	LDR      r6, [sp, #0x20]
	STR      r2, [r5]
	MOV      r2, #0
	ADD      r4, r3, #0
	STMIA    r3!, {r2}
	STR      r2, [r3]
	LDR      r2, [r1]
	LDR      r3, [r0]
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #4]
	SUB      r2, r2, r3
	SUB      r0, r1, r0
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r2, [sp]
	STR      r2, [sp, #8]
	ORR      r2, r1
	STR      r1, [sp, #0xc]
	BEQ      |loc_08019344|
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0xc]
	LSL      r0, r0, #8
	STR      r0, [sp]
	LDR      r0, [sp, #8]
	LSL      r1, r1, #8
	STR      r1, [sp, #4]
	ADD      r1, r0, #0
	MUL      r0, r1
	LDR      r1, [sp, #0xc]
	ADD      r2, r1, #0
	MUL      r1, r2
	ADD      r0, r0, r1
	ASR      r1, r0, #0x1f
	MOV      r2, #0x10
	BL       |inc_0x046118_0x049114| + 0xae4
	BL       |inc_0x03d784_0x041118| + 0x239a
	MOV      r1, #0x64
	MUL      r1, r0
	ADD      r0, r6, #0
	BL       |inc_0x046118_0x049114| + 0xd40
	ASR      r0, r0, #8
	ADD      r0, #1
	STR      r0, [r5]
	LDR      r1, [sp]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r4]
	LDR      r1, [sp, #4]
	LDR      r0, [r5]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r4, #4]
|loc_08019344|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	MOV      r1, #1
	STR      r1, [r0]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08019360|
	LDR      r1, [pc, #0x10c]
	STR      r1, [r0]
|loc_08019360|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r0, #0
	STR      r0, [r4]
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r2, #0
	BNE      |sub_08019382|
	ADD      r0, r1, #0
	BEQ      |loc_08019380|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08019380|
	POP      {r3, pc}
