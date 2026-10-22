	CODE16
|sub_0800DB64|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x16c]
	ADD      r4, r1, #0
	ADD      sp, r3
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r0, [r4, #0x24]
	ADD      r3, sp
	LDR      r1, [r1, #0x20]
	STR      r0, [r3, #0x18]
	STR      r1, [r3, #0x14]
	LDR      r0, [r4, #0x1c]
	LDR      r1, [r4, #0x18]
	STR      r0, [r3, #0x20]
	STR      r1, [r3, #0x1c]
	LDR      r2, [r4, #0x20]
	LDR      r3, [r4, #0x18]
	LDR      r0, [r4, #0x1c]
	SUB      r2, r2, r3
	MOV      r3, #1
	LDR      r1, [r4, #0x24]
	LSL      r3, r3, #0xc
	ADD      r3, sp
	SUB      r0, r1, r0
	STR      r0, [r3, #8]
	STR      r2, [r3, #4]
	LDR      r1, [r3, #8]
	STR      r1, [r3, #0x10]
	STR      r2, [r3, #0xc]
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x110]
	LDR      r3, [r3, #0x10]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	ADD      r0, sp, #0xc
	MUL      r2, r3
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x10]
	MOV      r1, #0
	CMP      r0, #0
	BLE      |loc_0800DC92|
	ADD      r6, r3, #0
	ADD      r6, #0x18
	STR      r6, [r3, #0x28]
	ADD      r6, #4
	ADD      r0, r6, #4
	MOV      lr, r0
	STR      r6, [r3, #0x24]
|loc_0800DBCC|
	LSL      r0, r1, #0x1d
	LSR      r0, r0, #0x1d
	MOV      ip, r0
	LDR      r0, [r4, #0x1c]
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r0, r0, r1
	STR      r0, [sp, #8]
	ADD      r3, sp
	LDR      r2, [r3, #0xc]
	MOV      r0, #0
	ASR      r7, r1, #3
	CMP      r2, #0
	BLE      |loc_0800DC84|
|loc_0800DBE8|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r6, [r3, #0x10]
	ASR      r2, r0, #3
	MUL      r6, r7
	ADD      r3, r6, #0
	ADD      r3, ip
	LSL      r6, r3, #3
	LSL      r2, r2, #6
	LSL      r5, r0, #0x1d
	LSR      r5, r5, #0x1d
	ADD      r2, r6, r2
	ADD      r2, r2, r5
	ADD      r5, sp, #0xc
	LDRB     r2, [r5, r2]
	CMP      r2, #0
	BEQ      |loc_0800DC76|
	LDR      r2, [r4, #0x18]
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r2, r2, r0
	STR      r2, [sp, #4]
	ADD      r3, sp
	LDR      r5, [r3, #0x14]
	CMP      r5, r2
	BGE      |loc_0800DC22|
	ADD      r3, #0x14
	B        |loc_0800DC24|
|loc_0800DC22|
	ADD      r3, sp, #4
|loc_0800DC24|
	LDR      r5, [r3]
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	STR      r5, [r3, #0x14]
	LDR      r5, [r3, #0x18]
	LDR      r6, [r3, #0x28]
	LDR      r3, [sp, #8]
	CMP      r5, r3
	BLT      |loc_0800DC3A|
	ADD      r6, sp, #8
|loc_0800DC3A|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r5, [r6]
	ADD      r3, sp
	STR      r5, [r3, #0x18]
	LDR      r6, [r3, #0x24]
	ADD      r2, #1
	STR      r2, [sp]
	LDR      r5, [r3, #0x1c]
	CMP      r5, r2
	BGT      |loc_0800DC52|
	MOV      r6, sp
|loc_0800DC52|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r2, [r6]
	ADD      r3, sp
	STR      r2, [r3, #0x1c]
	LDR      r2, [sp, #8]
	MOV      r6, lr
	ADD      r2, #1
	STR      r2, [sp]
	LDR      r5, [r3, #0x20]
	CMP      r5, r2
	BGT      |loc_0800DC6C|
	MOV      r6, sp
|loc_0800DC6C|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r2, [r6]
	ADD      r3, sp
	STR      r2, [r3, #0x20]
|loc_0800DC76|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r2, [r3, #0xc]
	ADD      r0, #1
	CMP      r2, r0
	BGT      |loc_0800DBE8|
|loc_0800DC84|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x10]
	ADD      r1, #1
	CMP      r0, r1
	BGT      |loc_0800DBCC|
|loc_0800DC92|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x18]
	LDR      r1, [r3, #0x20]
	ADD      r0, r0, r1
	ASR      r0, r0, #1
	STR      r0, [r3, #0x18]
	ADD      r0, r3, #0
	ADD      r0, #0x14
	LDR      r4, [r3, #0x2c]
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r4!, {r0, r1, r2, r3}
	LDR      r3, [pc, #0x28]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
|loc_0800DCB2|
	DCW      0x0000
	DCW      0x0000,0x0601,0x9680,0x0804,0x259c,0x0807,0xa85c,0x0804
	DCW      0x1afc,0x0300,0xffff,0x0000,0xe454,0x0804,0xffff
|loc_0800DCD2|
	DCW      0xfe00
	DCW      0xefd4,0xffff,0x1034
	LSL      r0, r0, #0
