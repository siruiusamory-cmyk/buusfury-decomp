	CODE16
|sub_08001808|
	MOV      r2, #0
	STR      r2, [sp]
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
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r6, r2, #0x18
	LSR      r6, r6, #0x18
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r7, [r0, #4]
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001860|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0xec]
	MOV      r2, #1
	STR      r1, [r0]
	STRB     r6, [r0, #8]
	STR      r4, [r0, #0x10]
	STR      r5, [r0, #0xc]
	LDR      r1, [sp]
	SUB      r1, r2, r1
	STR      r1, [r0, #0x14]
	LDR      r1, [sp, #4]
	STR      r1, [r0, #0x18]
	LDR      r1, [sp, #8]
	STR      r1, [r0, #0x1c]
|loc_08001860|
	ADD      r4, r0, #0
	ADD      r0, r7, #0
	BL       |loc_080001C6|
	MOV      r1, #0
	CMP      r0, #0
	BEQ      |loc_08001874|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08001874|
	LDR      r0, [pc, #0xac]
	ADD      r2, r1, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
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
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	MOV      r6, #0
	CMP      r0, #0
	BEQ      |loc_080018B2|
	LDR      r1, [pc, #0x8c]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
	STR      r6, [r0, #0xc]
|loc_080018B2|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080018C4|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_080018C4|
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
	BEQ      |loc_080018FE|
	LDR      r1, [pc, #0x44]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	STR      r4, [r0, #8]
|loc_080018FE|
	ADD      r4, r0, #0
	ADD      r0, r5, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_08001910|
	ADD      r6, r0, #0
	ADD      r6, #0xff
	ADD      r6, #0x8d
|loc_08001910|
	LDR      r0, [pc, #0x10]
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
|loc_0800191E|
	DCW      0x0000
	DCW      0xbf14,0x0804,0x4fbc,0x0805,0xdd30,0x0804,0xc828,0x0804
	DCW      0xc83c,0x0804,0xe268
|loc_08001936|
	LSR      r4, r0, #0x20
	LDMIA    r0!, {r4, r6}
	LSR      r4, r0, #0x20
	BLE      |loc_080019C8|
	LSR      r4, r0, #0x20
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
	BEQ      |loc_08001978|
	LDR      r1, [pc, #0x294]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r4, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_08001978|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_0800198A|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_0800198A|
	LDR      r0, [pc, #0x27c]
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
	BEQ      |loc_080019D0|
	LDR      r1, [pc, #0x244]
|loc_080019C8|
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r4, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_080019D0|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_080019E2|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_080019E2|
	LDR      r0, [pc, #0x224]
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
	BEQ      |loc_08001A28|
	LDR      r1, [pc, #0x1f0]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r4, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_08001A28|
	ADD      r4, r0, #0
	ADD      r0, r6, #0
	BL       |loc_080001C6|
	CMP      r0, #0
	BEQ      |loc_08001A3A|
	ADD      r7, r0, #0
	ADD      r7, #0xff
	ADD      r7, #0x8d
|loc_08001A3A|
	LDR      r0, [pc, #0x1cc]
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	ADD      r1, r0, #0
	LDR      r0, [r0]
	SUB      sp, #0xc
	SUB      r0, #1
	STR      r0, [r1]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	STR      r0, [sp, #8]
	LDR      r0, [r1]
	SUB      r0, #1
	STR      r0, [r1]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	STR      r0, [sp, #4]
	LDR      r2, [r1]
	SUB      r2, #1
	LSL      r0, r2, #2
	STR      r2, [r1]
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	SUB      r2, #1
	STR      r2, [r1]
	LSL      r2, r2, #2
	ADD      r1, r2, r1
	LDR      r4, [r1, #4]
	BL       |loc_080001C6|
	ADD      r1, r0, #0
	MOV      r0, #0
	ADD      r2, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x6fe
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |loc_080001C6|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001AA2|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_08001AA2|
	LDR      r0, [pc, #0x164]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r4, r5, lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	MOV      r3, #0x64
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	MOV      r2, #1
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
	BEQ      |loc_08001AFC|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_08001AFC|
	LDR      r0, [pc, #0x108]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {r4, r5, pc}
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
	MOV      r2, #1
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
	BEQ      |loc_08001B5E|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_08001B5E|
	LDR      r0, [pc, #0xa8]
	ADD      r1, r5, #0
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {r4, r5, pc}
|sub_08001B6C|
|unk_08001B6C|
	INCBIN	baserom.gba_0x1b6c_0x1b82.extracted
