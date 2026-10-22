	CODE16
|sub_08037564|
|unk_08037564|
		ADD r1, r2, #0
		ADD r1, #0x24
	INCBIN  baserom.gba_0x37568_0x3756a.extracted
|sub_0803756A|
|unk_0803756A|
	INCBIN	baserom.gba_0x3756a_0x3756e.extracted
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	ADD      r7, #0x40
	ADD      r4, r0, #0
	LDR      r2, [pc, #0x308]
	LDRB     r0, [r7]
	LDR      r2, [r2]
	LDR      r6, [pc, #0x304]
	LDR      r1, [pc, #0x308]
	SUB      r6, #0x24
	ADD      r5, r2, r1
	CMP      r0, #0
	SUB      sp, #0x4c
	BEQ      |sub_08037644|
	CMP      r0, #1
	BNE      |loc_0803759A|
	ADD      r1, r6, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
|loc_0803759A|
	MOV      r0, #0x3c
	STR      r0, [r4, #0x5c]
	MOV      r0, #2
	STRB     r0, [r7]
	ADD      r1, r4, #0
	ADD      r1, #0x28
	ADD      r0, sp, #0x44
	BL       |inc_0x049120_0x055620| + 0x67e0
	LDR      r0, [r4, #0x58]
	LDR      r1, [pc, #0x2d0]
	LSL      r0, r0, #2
	ADD      r1, #0x14
	LDR      r0, [r1, r0]
	MOV      r1, #0
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	ASR      r0, r0, #1
	STR      r0, [r4, #0x6c]
	ADD      r0, sp, #0x3c
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	LDR      r0, [r4, #0x6c]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x3c]
	LDR      r0, [r4, #0x6c]
	ADD      r2, sp, #8
	STR      r0, [sp, #0x40]
	LDR      r0, [r4, #0x1c]
	STR      r0, [sp, #0x28]
	LDRB     r0, [r4, #0x10]
	STRB     r0, [r3, #0x1c]
	LDR      r0, [pc, #0x2c0]
	STR      r0, [sp, #0x24]
	LDR      r1, [r4, #0x4c]
	LDR      r0, [r4, #0x60]
	LDR      r1, [r1, #0xc]
	LSL      r3, r1, #4
	SUB      r1, r3, r1
	LSL      r1, r1, #4
	ASR      r1, r1, #0x10
	MUL      r0, r1
	STR      r0, [sp, #0x20]
	LDR      r0, [sp, #0x44]
	LDR      r1, [sp, #0x3c]
	LDR      r3, [sp, #0x40]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x48]
	STR      r1, [sp]
	SUB      r0, r0, r3
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x10]
	STR      r1, [sp, #0xc]
	LDR      r1, [sp, #0x3c]
	LDR      r0, [sp, #0x44]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x48]
	STR      r1, [sp]
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x18]
	STR      r1, [sp, #0x14]
	LDRB     r0, [r4, #0x11]
	ADD      r3, sp, #0
	MOV      r1, #0
	STRB     r0, [r3, #8]
	LDR      r0, [pc, #0x260]
	STR      r4, [sp, #0x38]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	ADD      r1, r6, #0
	ADD      r1, #0xff
	ADD      r1, #0x15
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r1, sp, #0xc
	LDMIA    r1!, {r0, r1}
	ADD      r4, #0x64
	STMIA    r4!, {r0, r1}
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
