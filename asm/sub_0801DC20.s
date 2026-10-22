	CODE16
|sub_0801DC20|
	LDR      r6, [pc, #0x48]
	ADD      r3, sp, #0x100
	LDR      r0, [r6, #8]
	STR      r0, [sp, #0x128]
	MOV      r0, #0x78
	STRB     r5, [r3, #0x1c]
	STR      r0, [sp, #0x120]
	MOV      r0, #0x58
	STR      r0, [sp, #0x124]
	LDR      r0, [pc, #0x3c]
	STRB     r5, [r3, #0x1e]
	STR      r0, [sp, #0x13c]
	MOV      r0, #2
	STRB     r0, [r3, #0x1f]
	MOV      r0, #0xff
	ADD      r0, #0x25
	LDR      r1, [r7, r0]
	ADD      r0, sp, #0x11c
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r6, sp, #0x11c
	ADD      r1, r6, #0
	LDR      r0, [sp, #0x158]
	BL       |inc_0x0158_0x143f2| + 0x6594
	LDR      r1, [pc, #0x28]
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x11c
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x15c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	DCW      0xe9d8,0x0871,0xf5a5,0x0803
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	STRB     r0, [r2, #0x16]
	LSR      r3, r5, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	PUSH     {r4, r5, r6, r7}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x51
	MOV      r1, #0
	LDR      r2, [pc, #0x2f8]
	STR      r1, [r4]
	LDR      r2, [r2, #0xc]
	ADD      r2, #0xe4
	LDR      r3, [r2]
	CMP      r3, #0
	BLE      |loc_0801DCD0|
	ADD      r5, r4, #0
	LDR      r6, [pc, #0x2ec]
	SUB      r5, #0x50
|loc_0801DC9E|
	LSL      r0, r1, #2
	ADD      r0, r0, r2
	ADD      r0, #4
	LDR      r3, [r0]
	LSL      r7, r3, #4
	LSR      r7, r7, #4
	MOV      r3, #0x2c
	MUL      r3, r7
	ADD      r3, r3, r6
	LDRB     r3, [r3, #0x14]
	LDR      r7, [r5, #0x14]
	CMP      r3, r7
	BNE      |loc_0801DCC8|
	LDR      r3, [r4]
	ADD      r7, r3, #1
	LSL      r3, r3, #3
	STR      r7, [r4]
	LDR      r0, [r0]
	ADD      r3, r3, r4
	ADD      r3, #4
	STMIA    r3!, {r0, r1}
|loc_0801DCC8|
	LDR      r0, [r2]
	ADD      r1, #1
	CMP      r0, r1
	BGT      |loc_0801DC9E|
|loc_0801DCD0|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801DCD4|
|unk_0801DCD4|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		CMP r2, #8
		BHS      |loc_0801DCE6|
		DCW     0xA302
		ADD r3, r3, r2
		LDRH r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
|loc_0801DCE6|
		B        |loc_0801DDEC|
	INCBIN  baserom.gba_0x1dce8_0x1dd72.extracted
