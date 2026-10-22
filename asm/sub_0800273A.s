	CODE16
|sub_0800273A|
	MOV      r6, #0
	LDR      r0, [pc, #0x21c]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_080027DA|
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	STR      r0, [sp, #0xc]
	MOV      r0, #0
	STR      r1, [sp, #0x10]
	BL       |inc_0x049120_0x055620| + 0x746c
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r7, [pc, #0x1ec]
	LDR      r0, [r7, #0x18]
	BL       |loc_08011DB4|
	MOV      r0, #0xc1
	LSL      r0, r0, #2
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080027AE|
	MOV      r3, #0
	MOV      r2, #0xd
	MOV      r1, #7
	ADD      r0, r4, #0
	BL       |loc_08005460|
	LDR      r0, [pc, #0x1d8]
	ADD      r2, sp, #0xc
	STR      r0, [r4]
	MOV      r0, #5
	LSL      r0, r0, #7
	ADD      r0, r4, r0
	LDMIA    r2!, {r1, r2}
	STR      r1, [r0, #0x7c]
	ADD      r3, r0, #0
	ADD      r3, #0x80
	LDR      r0, [pc, #0x1c8]
	STR      r2, [r3]
	LDR      r0, [r0]
	MOV      r1, #0xff
	ADD      r1, #0xd
	STR      r0, [r1, r4]
	MOV      r0, #0xb
	LSL      r0, r0, #6
	ADD      r0, r4, r0
	STR      r6, [r0, #0x38]
|loc_080027AE|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x11c
	SUB      r1, r0, #1
	LDR      r0, [r5]
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r5
	STR      r2, [r5]
	STR      r1, [r0, #4]
	LDR      r0, [r7, #0x18]
	BL       |loc_08011E0E|
	MOV      r1, #1
	LDR      r0, [r7, #0x24]
	BL       |loc_0800938C|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7448
	BL       |inc_0x03d784_0x041118| + 0x11c
|loc_080027DA|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LDR      r0, [pc, #0x17c]
	PUSH     {r4, r5, r6, lr}
	LDR      r4, [r0]
	CMP      r4, #0
	BEQ      |loc_08002860|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x746c
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r5, [pc, #0x160]
	LDR      r0, [r5, #0x18]
	BL       |loc_08011DB4|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |sub_0802e83c|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      r6, r0, #0
	LDR      r0, [r5, #0x18]
	BL       |loc_08011E0E|
	CMP      r6, #2
	BNE      |loc_0800284E|
	LDR      r0, [r5, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x140]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800EDF8|
	ADD      r0, r4, #0
	BL       |loc_0801064C|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800284E|
	MOV      r1, #1
	LDR      r0, [r5, #0x24]
	BL       |loc_0800938C|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7448
	BL       |inc_0x03d784_0x041118| + 0x11c
|loc_08002860|
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r1, [pc, #0xf0]
	LDR      r4, [pc, #0xec]
	MOV      r0, #1
	STR      r0, [r1]
	LDR      r0, [r4, #0x18]
	BL       |loc_08011B04|
	LDR      r0, [r4, #0x28]
	BL       |loc_08012628|
	LDR      r1, [pc, #0xf0]
	LDR      r0, [r4, #4]
	ADD      r0, r0, r1
	BL       |inc_0x03d784_0x041118| + 0xb68
	BL       |inc_0x03d784_0x041118| + 0x16e
	MOV      r0, #0xff
|loc_08002888|
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080028AA|
	LDR      r1, [pc, #0xdc]
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r2, [r1, #0xc]
	STR      r2, [r1, #8]
	STR      r2, [r1, #0x10]
	LDR      r1, [pc, #0xcc]
	STR      r1, [r0]
|loc_080028AA|
	BL       |inc_0x03d784_0x041118| + 0xcc
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r1, r0, #0
	MOV      r3, #0x64
	MOV      r2, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x41b6
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x80]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
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
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r1, r0, #0
	ADD      r3, r5, #0
	ADD      r2, r4, #0
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x41b6
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x44]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, r4, r5, pc}
	LDR      r0, [pc, #0x38]
	PUSH     {r3, lr}
	MOV      r2, #0
	MOV      r1, #0x13
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C70|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x18]
	LDR      r0, [r0, #0x14]
	BL       |loc_0800441E|
	LDR      r1, [r4]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r4
	STR      r2, [r4]
	STR      r0, [r1, #4]
	POP      {r4, pc}
	LSL      r0, r0, #0
	LDMIA    r7!, {r2, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	CMP      r2, #0x58
	LSL      r0, r0, #0xc
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x10]
	LSR      r4, r0, #0x20
	ADD      r0, r2, r4
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADR      r4, |loc_08002988|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	LDR      r5, [pc, #0x270]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
|loc_08002988|
	LDR      r0, [r5, #0x14]
	ADD      r1, r4, #0
	BL       |loc_08004448|
|unk_08002990|
	INCBIN	baserom.gba_0x2990_0x2992.extracted
	MOV      r0, #0x14
|loc_08002994|
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_080029A8|
	LDR      r1, [pc, #0x254]
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	STR      r2, [r0, #8]
	STR      r4, [r0, #0xc]
|loc_080029A8|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x24c]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_080029B8|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_080029B8|
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
|sub_080029C0|
|unk_080029C0|
	INCBIN	baserom.gba_0x29c0_0x29c2.extracted
