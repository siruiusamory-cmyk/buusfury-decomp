	CODE16
|sub_08004DEE|
	LSR      r5, r0, #0x20
	LDMIA    r4!, {r2, r5, r7}
	LSR      r7, r6, #1
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	DCW      0xf754,0xffff
	LSR      r4, r5, #2
	LSL      r0, r0, #0
	LSL      r5, r3, #0x12
	LSR      r5, r0, #0x20
	LSR      r0, r5, #2
	LSL      r0, r0, #0
	LSL      r5, r7, #8
	LSR      r5, r0, #0x20
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08004E1C|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08004E24|
|loc_08004E1C|
	LDR      r1, [pc, #0xd8]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_08004E24|
	POP      {r3, pc}
	MOV      r2, #3
	LSL      r2, r2, #0xf
	PUSH     {r4, lr}
	MOV      r1, #0
	LSL      r0, r2, #0xa
	SUB      sp, #0x48
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	ADD      r0, sp, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0xb8]
	LDR      r1, [sp, #0x38]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r1, [pc, #0xb4]
	ADD      r0, sp, #0x14
	BL       |inc_0x03d784_0x041118| + 0x2234
	MOV      r0, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, #0x14
	MOV      r4, #0
	STR      r0, [sp, #0x10]
	ADD      r0, sp, #4
	STR      r4, [sp, #4]
	STR      r4, [sp, #8]
	MOV      r2, #1
	LDR      r1, [pc, #0xa0]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r0, [pc, #0x9c]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1, #0xe]
	STRH     r4, [r1, #0x1c]
	STRH     r4, [r1, #0x1e]
	LSR      r0, r1, #0xf
	STRH     r0, [r1]
	LDR      r0, [pc, #0x90]
	ADD      r1, #0x40
	STRH     r0, [r1, #0x10]
	LDR      r0, [pc, #0x90]
	LDR      r1, [pc, #0x90]
	STRB     r4, [r0]
	SUB      r0, #1
	STRB     r4, [r0]
	LSR      r2, r0, #0x11
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0x24
	LDR      r0, [pc, #0x68]
	SUB      r0, #4
	LDR      r0, [r0]
	MOV      r1, #0
	STRB     r4, [r0, #1]
	ADD      r0, sp, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x48
	POP      {r4, pc}
	LDR      r1, [r0, #4]
	ADD      r1, #1
	STR      r1, [r0, #4]
	LDR      r0, [pc, #0x68]
	CMP      r1, #0x10
	BGT      |loc_08004EB8|
	STRB     r1, [r0, #2]
	MOV      r0, #0
	BX       lr
|loc_08004EB8|
	CMP      r1, #0x96
	BGT      |loc_08004EC0|
	MOV      r0, #0
	BX       lr
|loc_08004EC0|
	CMP      r1, #0xa6
	BGT      |loc_08004ECE|
	MOV      r2, #0xa6
	SUB      r1, r2, r1
	STRB     r1, [r0, #2]
	MOV      r0, #0
	BX       lr
|loc_08004ECE|
	CMP      r1, #0xb4
	BGE      |sub_08004ED6|
	MOV      r0, #0
	BX       lr
