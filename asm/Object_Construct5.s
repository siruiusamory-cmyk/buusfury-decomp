	CODE16
|Object_Construct5|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_0800C0DC|
	MOV      r0, #0x50
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800C0DC|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800C0DC|
	LDR      r0, [pc, #0x194]
	MOV      r6, #0xf
	LSL      r6, r6, #8
	LDR      r5, [pc, #0x194]
	STR      r0, [r4]
	STRH     r6, [r4, #0xe]
	LDR      r0, [r5]
	ADD      r1, r6, #0
	BL       |loc_0801124C|
	ADD      r3, r0, #1
	BNE      |loc_0800C104|
	ADD      r1, r6, #0
	LDR      r0, [r5]
	BL       |sub_08011732|
	ADD      r1, r6, #0
	LDR      r0, [r5]
	BL       |loc_0801124C|
|loc_0800C104|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x174]
	MOV      r2, #0x10
	STR      r0, [r4]
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	MOV      r1, #0xf0
	ADD      r6, r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r0, #0
	STRB     r0, [r4, #0x10]
	STR      r0, [r4, #0x18]
	STR      r0, [r4, #0x14]
	STR      r0, [r4, #4]
	MOV      r0, #0x11
	STRB     r0, [r4, #8]
	LDR      r0, [r5, #4]
	MOV      r2, #1
	STR      r0, [r4, #0x28]
	MOV      r0, #0x78
	STR      r0, [r4, #0x20]
	MOV      r0, #0xb
	STR      r0, [r4, #0x24]
	MOV      r0, #2
	STRB     r0, [r4, #0x1f]
	LDR      r1, [pc, #0x144]
	STRB     r2, [r6, #2]
	STR      r1, [r6, #0x20]
	STRB     r2, [r4, #0x1c]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r1, [r0, #0x40]
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x138]
	SUB      sp, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [r5, #0x18]
	LDR      r1, [pc, #0x130]
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0xe
	LDR      r1, [r1, r0]
	ADD      r0, r5, #0
	ADD      r0, #0x1c
	ADD      r6, r0, #0
	BL       |inc_0x03d784_0x041118| + 0x356
	LDR      r0, [r5, #0x18]
	ADD      r7, sp, #4
	STR      r0, [r5, #0x14]
	LDR      r0, [pc, #0x108]
	ADD      r0, #8
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r7!, {r0, r1, r2, r3}
	SUB      r7, #0x10
	MOV      r4, #0
|loc_0800C178|
	LDRH     r0, [r5, #0xc]
	LDR      r1, [pc, #0x110]
	ADD      r2, r7, #0
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSL      r1, r4, #9
	ADD      r1, r0, r1
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x3c
	LDR      r0, [sp, #4]
	ADD      r4, #1
	ADD      r0, #0x20
	STR      r0, [sp, #4]
	LDR      r0, [sp, #0xc]
	ADD      r0, #0x20
	STR      r0, [sp, #0xc]
	CMP      r4, #7
	BLT      |loc_0800C178|
	MOV      r0, #0xf0
	STR      r0, [sp, #0xc]
	LDRH     r0, [r5, #0xc]
	LDR      r1, [pc, #0xe4]
	ADD      r2, r7, #0
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	MOV      r1, #7
	LSL      r1, r1, #9
	ADD      r1, r0, r1
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x3c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_0800C1BC|
|unk_0800C1BC|
		LDRB r1, [r0, #0x10]
		CMP r1, #0
		BEQ      |loc_0800C1D0|
		ADD r1, #0xff
		STRB r1, [r0, #0x10]
		LDR r1, [r0, #0x18]
		LDR r2, [r0, #0x14]
		CMP r1, r2
		BEQ      |loc_0800C1D0|
		B        |inc_0x0158_0x143f2| + 0xbfec
|loc_0800C1D0|
		BX       lr
