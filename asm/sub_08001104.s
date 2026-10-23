|sub_08001104|
	EXPORT |sub_08001104|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	MOV      r7, #0
	CMP      r0, #0
	BEQ      |loc_0800113C|
	LDR      r1, [pc, #0x260]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r4, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_0800113C|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_0800114E|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_0800114E|
	LDR      r0, [pc, #0x248]
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r2, [r0]
	ADD      r1, r0, #0
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r0, r2, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	SUB      r2, #1
	STR      r2, [r1]
	LSL      r2, r2, #2
	ADD      r1, r2, r1
	LDR      r5, [r1, #4]
	BL       |loc_080001C6|
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08001190|
	LDR      r1, [pc, #0x210]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_08001190|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080011A2|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080011A2|
	LDR      r0, [pc, #0x1f4]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	MOV      r7, #0
	CMP      r0, #0
	BEQ      |loc_080011E8|
	LDR      r1, [pc, #0x1c0]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r4, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_080011E8|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080011FA|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_080011FA|
	LDR      r0, [pc, #0x19c]
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r7, [r0, #4]
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800124C|
	LDR      r1, [pc, #0x164]
	MOV      r2, #0
	STMIA    r0!, {r1, r2, r4}
	SUB      r0, #0xc
	STR      r5, [r0, #0x14]
	STR      r6, [r0, #0x18]
	STR      r2, [r0, #0x20]
|loc_0800124C|
	ADD      r4, r0, #0
	ADD      r0, r7, #0
	BL       |loc_080001C6|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001260|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_08001260|
	LDR      r0, [pc, #0x134]
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08001298|
	LDR      r1, [pc, #0x114]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_08001298|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080012AA|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080012AA|
	LDR      r0, [pc, #0xec]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_080012E4|
	LDR      r1, [pc, #0xcc]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_080012E4|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080012F6|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080012F6|
	LDR      r0, [pc, #0xa0]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r2, [sp, #8]
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r2, [sp, #4]
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r7, [r0, #4]
	CMP      r5, #2
	BGE      |loc_08001346|
	MOV      r5, #2
|loc_08001346|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08001374|
	MOV      r0, #0
	STR      r0, [r4, #4]
	LDR      r0, [pc, #0x58]
	MOV      r1, #0xff
	STR      r0, [r4]
	STR      r6, [r4, #8]
	LDR      r0, [sp, #4]
	STR      r0, [r4, #0xc]
	LDR      r0, [sp, #8]
	STR      r0, [r4, #0x10]
	ASR      r0, r5, #1
	STR      r5, [r4, #0x14]
	STR      r0, [r4, #0x1c]
	STR      r5, [r4, #0x18]
	ADD      r1, #1
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r4, #0x20]
|loc_08001374|
	ADD      r0, r7, #0
	BL       |loc_080001C6|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001386|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_08001386|
	LDR      r0, [pc, #0x10]
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|loc_08001394|
	DCW      0xc428
	DCW      0x0804,0x4fbc,0x0805,0xae70,0x0804,0xc43c,0x0804,0xae84
	DCW      0x0804,0xab58,0x0804,0xc450,0x0804,0xc800
|loc_080013B2|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_080013D4|
	LDR      r1, [pc, #0x284]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
|loc_080013D4|
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080013E6|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080013E6|
	LDR      r0, [pc, #0x270]
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08001420|
	LDR      r1, [pc, #0x240]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_08001420|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_08001432|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_08001432|
	LDR      r0, [pc, #0x224]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_0800146C|
	LDR      r1, [pc, #0x1f8]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_0800146C|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_0800147E|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_0800147E|
	LDR      r0, [pc, #0x1d8]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r3, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	MOV      r2, #2
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0
	ADD      r1, sp, #4
	BL       |inc_0x049120_0x055620| + 0x770c
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |loc_080001C6|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_080014E0|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_080014E0|
	LDR      r0, [pc, #0x174]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r5, r2, #0x18
	LSR      r5, r5, #0x18
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	MOV      r7, #0
	CMP      r0, #0
	BEQ      |loc_0800152A|
	LDR      r1, [pc, #0x140]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STRB     r5, [r0, #8]
	STR      r4, [r0, #0xc]
|loc_0800152A|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_0800153C|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_0800153C|
	LDR      r0, [pc, #0x118]
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	ADD      r3, sp, #0
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRB     r1, [r3, #3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRB     r1, [r3, #2]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRB     r1, [r3, #1]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRB     r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0
	MOV      r1, sp
	BL       |sub_0802b8f0|
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |loc_080001C6|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_080015AE|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_080015AE|
	LDR      r0, [pc, #0xa8]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_080015E6|
	LDR      r1, [pc, #0x88]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STRB     r4, [r0, #8]
|loc_080015E6|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080015F8|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080015F8|
	LDR      r0, [pc, #0x5c]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08001632|
	LDR      r1, [pc, #0x40]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_08001632|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_08001644|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_08001644|
	LDR      r0, [pc, #0x10]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
|loc_08001652|
	DCW      0x0000
	DCW      0xae9c,0x0804,0x4fbc,0x0805,0xb2c8,0x0804,0xdea0,0x0804
	DCW      0xdd1c,0x0804,0xdec8
|loc_0800166A|
	LSR      r4, r0, #0x20
	LDMIA    r0!, {r2, r4}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r2, [sp]
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r7, [r0, #4]
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080016C4|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x268]
	STR      r1, [r0]
	LDR      r1, [sp]
	ADD      r0, #0xc
	STMIA    r0!, {r1, r4, r5}
	SUB      r0, #0x18
	STR      r6, [r0, #8]
|loc_080016C4|
	ADD      r4, r0, #0
	ADD      r0, r7, #0
	BL       |loc_080001C6|
	MOV      r1, #0
	CMP      r0, #0
	BEQ      |loc_080016D8|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_080016D8|
	LDR      r0, [pc, #0x248]
	ADD      r2, r1, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_08001712|
	LDR      r1, [pc, #0x21c]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STRB     r4, [r0, #8]
|loc_08001712|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_08001724|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_08001724|
	LDR      r0, [pc, #0x1fc]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	MOV      r7, #0
	CMP      r0, #0
	BEQ      |loc_0800176A|
	LDR      r1, [pc, #0x1c8]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r4, [r0, #0xc]
	STR      r5, [r0, #8]
|loc_0800176A|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_0800177C|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_0800177C|
	LDR      r0, [pc, #0x1a4]
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_080017B8|
	LDR      r1, [pc, #0x180]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #0xc]
	STR      r6, [r0, #8]
|loc_080017B8|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080017CA|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080017CA|
	LDR      r0, [pc, #0x158]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
|sub_080017D8|
|unk_080017D8|
	INCBIN	baserom.gba_0x17d8_0x1808.extracted
