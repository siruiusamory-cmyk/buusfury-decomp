	CODE16
|sub_08022902|
	LSL      r0, r0, #0
	MOV      r3, #0
	STRB     r3, [r1]
	LDR      r2, [r0, #4]
	STRH     r2, [r1, #2]
	LDR      r2, [r0, #8]
	STRH     r2, [r1, #4]
	LDR      r2, [r0, #0xc]
	STRB     r2, [r1, #6]
	LDR      r2, [r0, #0x10]
	STRB     r2, [r1, #7]
	LDR      r2, [r0, #0x14]
	STRB     r2, [r1, #8]
	LDR      r2, [r0, #0x18]
	STRB     r2, [r1, #9]
	MOV      r2, #0x2d
	STRB     r2, [r1, #0xa]
	MOV      r2, #1
	STRB     r2, [r1, #0xb]
	MOV      r2, #7
	STRB     r2, [r1, #0xc]
	STRB     r3, [r1, #0xd]
	LDRH     r0, [r0]
	STR      r0, [r1, #0x14]
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0x1347a
	STRB     r0, [r5]
	LDRB     r0, [r4, #0xc]
	STRB     r0, [r5, #1]
	LDRB     r0, [r4, #0x15]
	STRB     r0, [r5, #2]
	MOV      r0, #0
|loc_0802294C|
	ADD      r1, r4, r0
	LDRB     r2, [r1, #0xd]
	ADD      r1, r5, r0
	STRB     r2, [r1, #3]
	LSL      r2, r0, #1
	ADD      r2, r2, r4
	ADD      r2, #0x2e
	LDRB     r2, [r2]
	ADD      r0, #1
	CMP      r0, #6
	STRB     r2, [r1, #9]
	BLT      |loc_0802294C|
	LDRB     r0, [r4, #0x14]
	STRB     r0, [r5, #0xf]
	ADD      r0, r4, #0
	ADD      r0, #0x18
	LDRH     r0, [r0]
	STRH     r0, [r5, #0x10]
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	LDRH     r0, [r0]
	STRH     r0, [r5, #0x12]
	ADD      r0, r4, #0
	ADD      r0, #0x28
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0x29
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x15]
	ADD      r0, r4, #0
	ADD      r0, #0x2a
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x16]
	ADD      r0, r4, #0
	ADD      r0, #0x2b
	LDRB     r0, [r0]
	STRB     r0, [r5, #0x17]
	MOV      r0, #0
|loc_0802299A|
	LSL      r1, r0, #2
	ADD      r1, r1, r4
	ADD      r1, #0x3c
	LDR      r1, [r1]
	LSL      r2, r0, #1
	ADD      r2, r2, r5
	ADD      r0, #1
	CMP      r0, #4
	STRH     r1, [r2, #0x18]
	BLT      |loc_0802299A|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x68
	ADD      r5, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0xba4
	MOV      r0, #2
	STRB     r0, [r4]
	SUB      r0, #3
	STR      r0, [r4, #8]
	ADD      r6, r4, #0
	ADD      r6, #0x24
	LDRB     r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x13220
|loc_080229D0|
	STR      r0, [r6]
	LDR      r1, [r6]
	CMP      r1, r0
	BNE      |loc_080229D0|
	LDRB     r0, [r5, #1]
	MOV      r1, #0
	STRB     r0, [r4, #0xc]
	LDRB     r0, [r5, #2]
	STRB     r0, [r4, #0x15]
|loc_080229E2|
	ADD      r2, r5, r1
	LDRB     r0, [r2, #3]
	ADD      r3, r4, r1
	STRB     r0, [r3, #0xd]
	LSL      r0, r1, #1
	LDRB     r2, [r2, #9]
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	ADD      r6, r2, #0
|loc_080229F4|
	STRB     r2, [r0]
	LDRB     r3, [r0]
	CMP      r3, r2
	BNE      |loc_080229F4|
|loc_080229FC|
	STRB     r6, [r0, #1]
	LDRB     r2, [r0, #1]
	CMP      r2, r6
	BNE      |loc_080229FC|
	ADD      r1, #1
	CMP      r1, #6
	BLT      |loc_080229E2|
	MOV      r3, #0x10
	LDRSH    r6, [r5, r3]
	ADD      r0, r4, #0
	ADD      r0, #0x16
	ADD      r1, r6, #0
|loc_08022A14|
	STRH     r1, [r0]
	MOV      r3, #0
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A14|
	LSL      r1, r6, #0x10
	ASR      r1, r1, #0x10
|loc_08022A22|
	STRH     r1, [r0, #2]
	MOV      r3, #2
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A22|
	MOV      r3, #0x12
	LDRSH    r6, [r5, r3]
	ADD      r0, r4, #0
	ADD      r0, #0x1a
	ADD      r1, r6, #0
|loc_08022A36|
	STRH     r1, [r0]
	MOV      r3, #0
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A36|
	LSL      r1, r6, #0x10
	ASR      r1, r1, #0x10
|loc_08022A44|
	STRH     r1, [r0, #2]
	MOV      r3, #2
	LDRSH    r2, [r0, r3]
	CMP      r2, r1
	BNE      |loc_08022A44|
	LDRB     r1, [r5, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0x28
|loc_08022A54|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A54|
	LDRB     r1, [r5, #0x15]
	ADD      r0, r4, #0
	ADD      r0, #0x29
|loc_08022A62|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A62|
	LDRB     r1, [r5, #0x16]
	ADD      r0, r4, #0
	ADD      r0, #0x2a
|loc_08022A70|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A70|
	LDRB     r1, [r5, #0x17]
	ADD      r0, r4, #0
	ADD      r0, #0x2b
|loc_08022A7E|
	STRB     r1, [r0]
	LDRB     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08022A7E|
	LDRB     r0, [r5, #0xf]
	STRB     r0, [r4, #0x14]
	MOV      r0, #0
|loc_08022A8C|
	LSL      r1, r0, #2
	ADD      r1, r1, r4
	ADD      r1, #0x3c
	LSL      r2, r0, #1
	ADD      r2, r2, r5
	MOV      r3, #0x18
	LDRSH    r2, [r2, r3]
|loc_08022A9A|
	STR      r2, [r1]
	LDR      r3, [r1]
	CMP      r3, r2
	BNE      |loc_08022A9A|
	ADD      r0, #1
	CMP      r0, #4
	BLT      |loc_08022A8C|
	LDRB     r0, [r4, #0x14]
	LDR      r1, [pc, #0x288]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1e
	LSR      r2, r0, #0x1f
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	CMP      r2, #0
	BEQ      |loc_08022AD2|
	LDRH     r3, [r0]
	ADD      r2, r0, #4
	LSL      r3, r3, #0x10
	LSR      r3, r3, #0x10
|loc_08022ACA|
	STRH     r3, [r2]
	LDRH     r5, [r2]
	CMP      r5, r3
	BNE      |loc_08022ACA|
|loc_08022AD2|
	LDRB     r2, [r4, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LSL      r2, r2, #3
	ADD      r1, r2, r1
	LDRB     r1, [r1]
	LSL      r1, r1, #0x1f
	BEQ      |loc_08022AF4|
	LDRH     r0, [r0]
	ADD      r1, r4, #0
	ADD      r1, #0x1e
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_08022AEC|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_08022AEC|
|loc_08022AF4|
	POP      {r4, r5, r6, pc}
|loc_08022AF6|
	PUSH     {r4, r5, lr}
	LDR      r4, [pc, #0x23c]
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x1c]
	SUB      sp, #0x14
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x224]
	LDR      r0, [pc, #0x228]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x220]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x15
	LSL      r2, r2, #7
	MOV      r1, #0
	LDR      r0, [pc, #0x218]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0xc
	STR      r0, [sp, #4]
	MOV      r0, #9
	STR      r0, [sp, #8]
	MOV      r0, #0x12
	STR      r0, [sp, #0xc]
	MOV      r0, #0x10
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	LDR      r2, [pc, #0x204]
	LDR      r1, [pc, #0x1f8]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x200]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xa]
	ADD      r1, #0xfd
	STRH     r1, [r0, #8]
	MOV      r1, #0x4d
	LSL      r1, r1, #6
	STRH     r1, [r0]
	MOV      r0, #1
	ADD      r5, #0xff
	ADD      r5, #0x41
	STRB     r0, [r5]
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1e4]
	LDR      r5, [pc, #0x1c4]
	SUB      sp, #0x14
	LDR      r2, [pc, #0x1dc]
	ADD      r0, r4, r0
	LDR      r1, [r5, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [r5, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x41a4
	MOV      r0, #0xff
	LDR      r7, [pc, #0x1d0]
	ADD      r0, #0xa1
	LDR      r3, [r7, r0]
	LDR      r2, [r5, #8]
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #0x75
	STR      r2, [sp, #0xc]
	MOV      r2, #0x78
	STR      r0, [sp, #4]
	MOV      r3, #0x26
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r0, #0xff
	ADD      r0, #0xa5
	LDR      r3, [r7, r0]
	LDR      r2, [r5, #8]
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r3, [sp]
	MOV      r0, #0x75
	STR      r2, [sp, #0xc]
	MOV      r2, #0x78
	STR      r0, [sp, #4]
	MOV      r3, #0x82
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [r7, #0x68]
	LDR      r6, [r7, #0x5c]
	STR      r0, [sp, #0x10]
	LDR      r0, [r5, #8]
	ADD      r1, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x2864
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	ADD      r7, r0, #0
	MOV      r2, #0x84
	STR      r2, [sp]
	MOV      r0, #0
	MOV      r1, #1
	STR      r1, [sp, #8]
	MOV      r2, #0
	ADD      r7, #0x1e
	MOV      r3, #0xc
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r5, #8]
	STR      r6, [sp]
	MOV      r6, #0x90
	MOV      r1, #0
	STR      r1, [sp, #8]
	ADD      r3, r6, #0
	MOV      r0, #5
	STR      r2, [sp, #0xc]
	MOV      r2, #0x1c
	STR      r0, [sp, #4]
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #0
	STR      r2, [sp, #0xc]
	MOV      r1, #1
	MOV      r2, #0x84
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #8]
	ADD      r3, r7, #0
	ADD      r1, r4, #0
	MOV      r2, #1
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r2, [r5, #8]
	MOV      r1, #0
	STR      r2, [sp, #0xc]
	LDR      r2, [sp, #0x10]
	STR      r1, [sp, #8]
	STR      r2, [sp]
	ADD      r2, r7, #0
	ADD      r2, #0x10
	MOV      r0, #5
	ADD      r3, r6, #0
	ADD      r1, r4, #0
	STR      r0, [sp, #4]
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13fcc
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x56
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #4
	STR      r0, [sp, #4]
	MOV      r2, #4
	ADD      r1, r4, #0
	MOV      r3, #0xb
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #1
	STR      r0, [r6, #0x14]
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	MOV      r2, #1
	STR      r2, [sp, #0xc]
	MOV      r2, #0x56
	MOV      r1, #1
	STR      r1, [sp, #8]
	STR      r2, [sp]
	MOV      r0, #5
	STR      r0, [sp, #4]
	MOV      r2, #5
	ADD      r1, r4, #0
	MOV      r3, #0xd6
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x13d0c
	ADD      r1, r0, #0
	STR      r0, [r6, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x64f6
	ADD      r0, r4, #0
	BL       |loc_08022AF6|
	MOV      r0, #0
	STR      r0, [r6, #0x1c]
	STR      r0, [r6, #0x28]
	LDR      r0, [r5, #0x10]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_08022D24|
	LDR      r0, [pc, #0x80]
	MOV      r5, #0
	ADD      r7, r4, r0
|loc_08022CE4|
	MOV      r0, #0x68
	MUL      r0, r5
	LDR      r1, [pc, #0x78]
	ADD      r0, r0, r4
	ADD      r0, r0, r1
	LDRB     r1, [r0]
	LSL      r2, r1, #0x1f
	BEQ      |loc_08022D1E|
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	BEQ      |loc_08022D1E|
	LDR      r1, [r7]
	ADD      r2, r1, #1
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r6, r1, r7
	ADD      r6, #4
	STR      r2, [r7]
	STR      r5, [r6, #8]
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x24]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	STR      r0, [r6]
|loc_08022D1E|
	ADD      r5, #1
	CMP      r5, #9
	BLT      |loc_08022CE4|
|loc_08022D24|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7500
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08022D32|
	DCW      0x0000
	DCW      0x82ec,0x086b,0xbfa8,0x0872,0x652c,0x0805,0x0200,0x0500
	DCW      0xf800
|sub_08022D46|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	LSR      r0, r5, #2
	LSL      r0, r0, #0
	LSL      r4, r6, #0x17
	LSL      r0, r0, #0
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	LSL      r4, r0, #0x16
	LSL      r0, r0, #0
	LSR      r4, r5, #0xb
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	MOV      r2, #1
	LSL      r2, r2, #0x1a
	ADD      r4, r0, #0
	LDRH     r0, [r2]
	LSR      r1, r2, #0x12
	LDR      r5, [pc, #0x310]
	BIC      r0, r1
	STRH     r0, [r2]
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11458
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [pc, #0x300]
	LDR      r2, [pc, #0x2fc]
	ADD      r1, r4, r0
	LDR      r0, [r5, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BEQ      |loc_08022DA8|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08022DA8|
	POP      {r3, r4, r5, pc}
|loc_08022DAA|
	LDR      r2, [pc, #0x2dc]
	PUSH     {r4, lr}
	LDR      r2, [r2, #0x10]
	LDR      r4, [pc, #0x2e0]
	LDRB     r2, [r2]
	CMP      r2, #0
	BEQ      |loc_08022DD8|
	CMP      r2, #1
	BNE      |sub_08022DF0|
	LSL      r0, r1, #3
	SUB      r0, r0, r1
	LDR      r1, [pc, #0x2c4]
	LSL      r0, r0, #2
	ADD      r1, #0x24
	LDRH     r0, [r1, r0]
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r2, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xea08
	POP      {r4, pc}
|loc_08022DD8|
	LDR      r2, [pc, #0x2bc]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r0, r0, r2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	ADD      r2, r4, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xea08
	POP      {r4, pc}
