	CODE16
|sub_080240E0|
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0x2c]
	STRB     r0, [r1]
	MOV      r0, #1
	BX       lr
	MOV      r1, #0xff
	ADD      r1, #0x31
	LDRB     r1, [r1, r0]
	CMP      r1, r2
	BNE      |loc_0802410A|
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r0, #0x2c]
	ADD      r1, #1
	STR      r1, [r0, #0x2c]
	CMP      r1, #4
	BLE      |loc_0802410A|
	LDR      r1, [pc, #0x10]
	MOV      r0, #1
	STR      r0, [r1]
|loc_0802410A|
	BX       lr
|sub_0802410C|
	DCW      0x92ec
	DCW      0x0804,0xffff
|sub_08024112|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x270]
	LSR      r4, r0, #0x20
|loc_08024120|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x1b4]
	SUB      sp, #0x14
	LDR      r7, [r5, #0x68]
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r1, #1
	MOV      r2, #0x1c
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r4, r0, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r3, #0xc
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r6, [pc, #0x18c]
	MOV      r1, #0
	LDR      r2, [r6]
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r3, #0x28
	MOV      r0, #0
	STR      r7, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0xff
	ADD      r0, #0x15
	LDRB     r0, [r0, r4]
	MOV      r3, #0x10
	CMP      r0, #0
	BEQ      |sub_080241F6|
	CMP      r0, #1
	BEQ      |loc_0802421E|
	CMP      r0, #2
	BEQ      |loc_08024246|
	CMP      r0, #3
	BNE      |loc_080241AE|
	MOV      r0, #0xff
	ADD      r0, #0x75
	LDR      r5, [r5, r0]
	LDR      r2, [r6]
	MOV      r1, #0
	STR      r1, [sp, #8]
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x10
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	STR      r5, [sp]
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
|loc_080241AE|
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x128]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x77
	LSL      r2, r2, #6
	MOV      r1, #0
	LDR      r0, [pc, #0x120]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #7
	STR      r0, [sp, #4]
	MOV      r0, #8
	STR      r0, [sp, #8]
	MOV      r0, #0x18
	STR      r0, [sp, #0xc]
	MOV      r0, #0xf
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x10c]
	LDR      r1, [pc, #0x104]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r1, #0x3f
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	LSL      r1, r1, #7
	STRH     r1, [r0, #8]
	LDRH     r1, [r0]
	LSR      r2, r0, #0x12
	ORR      r1, r2
	STRH     r1, [r0]
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
