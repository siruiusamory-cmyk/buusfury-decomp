	CODE16
|sub_08002C58|
	MOV      r2, #0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4}
	LDR      r1, [r0]
	MOV      r3, #0x68
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r4, [r2, #4]
	LDR      r2, [pc, #0x230]
	MUL      r3, r4
	LDR      r2, [r2, #0x14]
	ADD      r2, r3, r2
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r2, r2, r3
	LDRB     r2, [r2, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x220]
	LSL      r2, r2, #3
	ADD      r2, r2, r3
	ADD      r3, r1, #1
	LDRH     r2, [r2, #0xe]
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	LDR      r7, [pc, #0x204]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	LDR      r0, [r7, #0x14]
	MOV      r4, #0
	LDRB     r0, [r0]
	CMP      r0, r5
	BNE      |loc_08002CE8|
	MOV      r3, #0x68
	LDR      r1, [r7, #0x14]
	MUL      r0, r3
	ADD      r0, r0, r1
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x1d8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
	LDR      r0, [pc, #0x1cc]
	LDR      r4, [r0]
|loc_08002CE8|
	MOV      r1, #0x68
	MUL      r1, r5
	LDR      r0, [r7, #0x14]
	MOV      r5, #0x9f
	LSL      r5, r5, #3
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	ADD      r1, r6, #0
	BL       |loc_08013DD6|
	CMP      r4, #0
	BEQ      |loc_08002D3C|
	ADD      r0, r6, #0
	BL       |sub_08000158|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800EDF8|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	BL       |loc_08010DAA|
	LDR      r0, [r7, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x180]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
|loc_08002D3C|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      sp, #0x10
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	ADD      r1, r0, #0
	LDR      r0, [r4]
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r2, [r4]
	STR      r1, [r0, #4]
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      sp, #0x10
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	LDR      r0, [r4]
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r2, [r4]
	STR      r1, [r0, #4]
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	LDRB     r2, [r0, #0x10]
	LDR      r0, [r4]
	ADD      r1, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r1, [r4]
	STR      r2, [r0, #4]
	POP      {r4, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	MOV      r3, #0
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	ADD      r2, sp, #4
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0xa8]
	STR      r0, [sp, #4]
	ADD      r1, #0x44
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7570
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x98]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	MOV      r3, #0
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	ADD      r2, sp, #4
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x6c]
	STR      r0, [sp, #4]
	ADD      r1, #0x50
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7570
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x5c]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0x14
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0x10]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	ADD      r1, sp, #4
	STR      r0, [sp, #4]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xb5ee
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	ADD      sp, #0x14
	POP      {pc}
	LSL      r0, r0, #0
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r1, [r0, #4]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xb9be
	BL       |inc_0x03d784_0x041118| + 0x11c
	SUB      r1, r0, #1
	LDR      r0, [r4]
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r2, [r4]
	STR      r1, [r0, #4]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	SUB      r1, #1
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	LSL      r3, r1, #2
	STR      r1, [r0]
	ADD      r3, r3, r0
	LDR      r6, [r3, #4]
	SUB      r1, #1
	LSL      r3, r1, #2
	STR      r1, [r0]
	ADD      r3, r3, r0
	LDR      r5, [r3, #4]
	SUB      r1, #1
	LSL      r3, r1, #2
	STR      r1, [r0]
	ADD      r3, r3, r0
	LDR      r7, [r3, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	ADD      r3, r2, #1
	BEQ      |loc_08002F22|
	LSL      r3, r2, #4
	SUB      r2, r3, r2
	LSL      r2, r2, #2
|loc_08002F22|
	MOV      r3, #0x68
	LDR      r0, [pc, #0x28c]
	MUL      r1, r3
	LDR      r4, [r0, #0x14]
	ADD      r3, r1, r4
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r4, r3, r1
	MOV      r3, #0x68
	STR      r2, [r4, #8]
	LDR      r2, [r0, #0x14]
	MUL      r3, r5
	ADD      r2, r3, r2
	MOV      r3, #0x68
	LDR      r0, [r0, #0x14]
	MUL      r3, r6
	ADD      r0, r3, r0
	ADD      r2, r2, r1
	ADD      r1, r0, r1
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	ADD      r3, r7, #0
	ADD      r0, r4, #0
	BL       |Stats_FuseRecord|
	LDRB     r0, [r4]
	MOV      r1, #1
	ORR      r0, r1
	MOV      r1, #2
	ORR      r0, r1
	STRB     r0, [r4]
	LDRB     r0, [r6]
	LSR      r0, r0, #1
	LSL      r0, r0, #1
	STRB     r0, [r6]
	LDRB     r0, [r5]
	LSR      r0, r0, #1
	LSL      r0, r0, #1
	STRB     r0, [r5]
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r3, #1
	LSL      r3, r3, #0x1b
	MOV      r1, #0
	MOV      r0, #0
|loc_08002F7C|
	ADD      r2, r0, r3
	LDRB     r2, [r2]
	ADD      r0, #1
	ADD      r1, r2, r1
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	CMP      r0, #0xa0
	BLT      |loc_08002F7C|
	CMP      r1, #0x33
	BEQ      |loc_08002F96|
	LDR      r1, [pc, #0x224]
	MOV      r0, #1
	STR      r0, [r1]
|loc_08002F96|
	MOV      r0, #0
	BL       |sub_0802b9a8|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x214]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	ADD      r2, sp, #4
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	MOV      r1, #0x1b
	STR      r0, [sp, #4]
	LDR      r0, [pc, #0x1e4]
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C0C|
	ADD      sp, #0xc
	POP      {pc}
	LDR      r0, [pc, #0x1d8]
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	BL       |loc_08008AFE|
	POP      {r3, pc}
	LDR      r1, [pc, #0x1cc]
	LDR      r2, [r0]
	LDR      r1, [r1, #0x14]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDRB     r2, [r1, #1]
	MOV      r3, #4
	LDR      r0, [r0, #4]
	ORR      r2, r3
	STRB     r2, [r1, #1]
	LSL      r3, r0, #4
	SUB      r0, r3, r0
	MOV      r2, #0x13
	LSL      r2, r2, #6
	LSL      r0, r0, #2
	ADD      r1, r1, r2
	STR      r0, [r1, #0x14]
	BX       lr
	LDR      r0, [pc, #0x1a4]
	MOV      r2, #4
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0, #1]
	BIC      r1, r2
	STRB     r1, [r0, #1]
	BX       lr
	PUSH     {r3, lr}
	MOV      r1, #0
	MOV      r0, #0
	BL       |loc_0802faba| + 0x1e6
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x18c]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
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
	LDR      r0, [r0, #4]
	ADD      r1, sp, #4
	BL       |inc_0x2bb4c_0x2d1c0| + 0x470
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x14c]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	ADD      sp, #0xc
	POP      {pc}
	LDR      r0, [pc, #0x140]
	PUSH     {r3, lr}
	MOV      r2, #0
	MOV      r1, #0x27
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C0C|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08003090|
	LDR      r1, [pc, #0x130]
	STR      r1, [r0]
	MOV      r1, #1
	STR      r1, [r0, #4]
|loc_08003090|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
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
	LDR      r1, [pc, #0xf0]
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0x10]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, sp, #4
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0xd4]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDR      r1, [pc, #0xd4]
	LDR      r1, [r1]
	BL       |sub_08012588|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [pc, #0xc4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0xa4]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDR      r1, [r2]
	BL       |sub_08012588|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [pc, #0x98]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x68]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDR      r1, [r2]
	BL       |sub_08012588|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [pc, #0x58]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x18]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDR      r1, [r2]
	BL       |sub_08012588|
	POP      {r3, pc}
|loc_080031B2|
	DCW      0x0000
	DCW      0x4fbc,0x0805,0x1004,0x0300,0x9978,0x0804,0xb704
|loc_080031C2|
	LSR      r1, r7, #1
	ASR      r0, r6, #0x20
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [pc, #0x270]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x228]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDR      r1, [r2]
	BL       |sub_08012588|
	POP      {r3, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0x6c
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x20c]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	LDR      r0, [pc, #0x200]
	LDR      r2, [r0]
	MOV      r0, sp
	BL       |loc_08004098|
	ADD      sp, #0x6c
	POP      {pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0x6c
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	LDR      r2, [pc, #0x1e8]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x1d4]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	LDR      r2, [r2]
	MOV      r0, sp
	BL       |loc_08004098|
	ADD      sp, #0x6c
	POP      {pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0x6c
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	LDR      r2, [pc, #0x1b4]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3, #4]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r3, [r2]
	STR      r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x190]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	LDR      r2, [r2]
	MOV      r0, sp
	BL       |loc_08004098|
	ADD      sp, #0x6c
	POP      {pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0]
	MOV      r6, #0
	SUB      r0, #1
	LSL      r1, r0, #2
	STR      r0, [r5]
	ADD      r1, r1, r5
	LDR      r7, [r1, #4]
	SUB      r0, #1
	STR      r0, [r5]
	LSL      r0, r0, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	MOV      r4, #0
	CMP      r7, #0
	STR      r0, [sp]
	BLE      |loc_08003302|
|loc_080032E6|
	LDR      r0, [sp]
	ADD      r1, r0, r4
	LDR      r0, [pc, #0x15c]
	LDR      r0, [r0, #0x14]
	BL       |loc_08004364|
	CMP      r0, #0
	BEQ      |loc_080032FC|
	MOV      r0, #1
	LSL      r0, r4
	ORR      r6, r0
|loc_080032FC|
	ADD      r4, #1
	CMP      r4, r7
	BLT      |loc_080032E6|
|loc_08003302|
	LDR      r0, [r5]
	ADD      r1, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r5
	STR      r1, [r5]
	STR      r6, [r0, #4]
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08003310|
|unk_08003310|
	INCBIN	baserom.gba_0x3310_0x3348.extracted
