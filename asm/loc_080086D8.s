	CODE16
|loc_080086D8|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	ADD      r4, #0x10
	SUB      sp, #0x20
	STR      r4, [sp, #0x1c]
	LDR      r3, [r0, #0x58]
	ADD      r6, r1, #0
	ADD      r6, #8
	LDR      r2, [r1, #0x10]
	MOV      ip, r6
	CMP      r3, r2
	BNE      |loc_080086FA|
	MOV      r6, ip
	LDR      r3, [r0, #0x5c]
	LDR      r4, [r6]
	CMP      r3, r4
	BEQ      |loc_08008794|
|loc_080086FA|
	MOV      r6, ip
	STR      r2, [r0, #0x58]
	LDR      r3, [r6]
	MOV      r2, #0x38
	STR      r3, [r0, #0x5c]
|loc_08008704|
	LSL      r3, r2, #1
	LDR      r4, [pc, #0x134]
	STR      r3, [sp, #0x18]
	LDRSH    r3, [r4, r3]
	LDR      r4, [sp, #0x1c]
	LDR      r4, [r4]
	ADD      r3, r4, r3
	ASR      r6, r3, #0xa
	LSL      r4, r6, #0x18
	LSR      r5, r4, #0x16
	ADD      r7, r6, #0
	ADD      r6, #1
	LDR      r4, [pc, #0x120]
	STR      r3, [sp, #4]
	LSL      r6, r6, #0x18
	LSR      r6, r6, #0x16
	LDR      r5, [r4, r5]
	LDR      r4, [r4, r6]
	LSL      r3, r3, #0x16
	MOV      lr, r4
	MOV      r4, #1
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	SUB      r4, r4, r3
	ADD      r6, r4, #0
	MUL      r6, r5
	MOV      r5, lr
	MUL      r5, r3
	ADD      r5, r6, r5
	STR      r6, [sp]
	MOV      r6, ip
	LDR      r6, [r6]
	ASR      r5, r5, #0x10
	MUL      r6, r5
	ASR      r5, r6, #0xa
	ADD      r6, r7, #0
	ADD      r6, #0x40
	MOV      lr, r6
	LSL      r6, r6, #0x18
	LDR      r7, [pc, #0xf0]
	LSR      r6, r6, #0x16
	LDR      r7, [r7, r6]
	MOV      r6, lr
	ADD      r6, #1
	STR      r7, [sp]
	LDR      r7, [pc, #0xe4]
	LSL      r6, r6, #0x18
	LSR      r6, r6, #0x16
	LDR      r6, [r7, r6]
	LDR      r7, [sp]
	MUL      r3, r6
	MUL      r4, r7
	ADD      r3, r4, r3
	ASR      r3, r3, #0x10
	LSL      r4, r2, #2
	ADD      r6, r4, r0
	MOV      r4, #0x7f
	MUL      r3, r5
	ASR      r3, r3, #0xa
	MVN      r4, r4
	STR      r3, [r4, r6]
	LDR      r3, [sp, #0x18]
	LDR      r4, [pc, #0xc4]
	ADD      r2, #1
	LDRH     r3, [r4, r3]
	MOV      r4, #0xff
	ADD      r4, #0x21
	MUL      r3, r5
	ASR      r3, r3, #0xa
	STR      r3, [r4, r6]
	CMP      r2, #0xa0
	BLT      |loc_08008704|
|loc_08008794|
	ADD      r3, r1, #0
	ADD      r3, #0x44
	MOV      ip, r3
	ADD      r3, #8
	STR      r3, [sp, #8]
	ADD      r3, #4
	STR      r3, [sp, #0x14]
	LDR      r3, [pc, #0x94]
	MOV      r5, ip
	ADD      r5, #4
	STR      r5, [sp, #0x10]
	SUB      r3, #8
	LDR      r3, [r3, #4]
	MOV      r2, #0x38
	ADD      r3, #0x80
	STR      r3, [sp, #0xc]
|loc_080087B4|
	LSL      r3, r2, #2
	MOV      r4, #0x7f
	MVN      r4, r4
	ADD      r3, r3, r0
	LDR      r4, [r4, r3]
	LDR      r5, [sp, #0x10]
	ADD      r3, #0xff
	LDR      r5, [r5]
	LDR      r6, [r1]
	MUL      r5, r4
	ASR      r5, r5, #0xa
	SUB      r5, r6, r5
	ASR      r7, r5, #2
	LDR      r5, [sp, #0x14]
	ADD      r3, #0x21
	LDR      r5, [r5]
	MUL      r5, r4
	ASR      r4, r5, #0xa
	LDR      r5, [r1, #4]
	SUB      r4, r5, r4
	ASR      r5, r4, #2
	LDR      r4, [r3]
	MOV      r3, ip
	LDR      r3, [r3]
	MOV      lr, r5
	MUL      r3, r4
	ADD      r5, r3, #0
	LSL      r3, r5, #2
	ADD      r3, r3, r5
	LSL      r3, r3, #1
	ASR      r5, r3, #0x17
	LDR      r3, [sp, #8]
	LDR      r3, [r3]
	MUL      r3, r4
	ADD      r6, r3, #0
	LSL      r3, r6, #2
	ADD      r3, r3, r6
	LSL      r3, r3, #1
	ASR      r6, r3, #0x17
	LDR      r3, [sp, #0xc]
	LSL      r4, r2, #4
	LDR      r3, [r3, #0x28]
	ADD      r2, #1
	ADD      r4, r3, r4
	LSL      r3, r5, #4
	SUB      r3, r3, r5
	LSL      r3, r3, #3
	SUB      r3, r7, r3
	STR      r3, [r4, #8]
	STMIA    r4!, {r5, r6}
	LSL      r3, r6, #4
	SUB      r3, r3, r6
	LSL      r3, r3, #3
	MOV      r5, lr
	SUB      r3, r5, r3
	SUB      r4, #8
	STR      r3, [r4, #0xc]
	CMP      r2, #0xa0
	BLT      |loc_080087B4|
	ADD      sp, #0x20
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	DCW      0xf000,0x0600
	LSL      r4, r2, #3
	LSL      r0, r0, #0x10
	ASR      r0, r4, #0x20
	LSR      r7, r0, #0x20
	ASR      r0, r4, #0x10
	LSR      r7, r0, #0x20
	STRB     r4, [r5, #0xb]
	LSR      r3, r7, #1
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	ASR      r0, r4, #0x15
	LSR      r7, r0, #0x20
	PUSH     {r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0xc
	ASR      r0, r0, #0x12
	STR      r0, [sp, #4]
	LDR      r0, [r1, #4]
	ADD      r4, r1, #0
	ASR      r0, r0, #0x12
	STR      r0, [sp, #8]
	ADD      r0, r5, #0
	ADD      r1, sp, #4
	BL       |loc_08008598|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_08008192|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_080086D8|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0xc
	ASR      r0, r0, #0x12
	STR      r0, [sp, #4]
	LDR      r0, [r1, #4]
	ADD      r5, r1, #0
	ASR      r0, r0, #0x12
	STR      r0, [sp, #8]
	LDR      r0, [sp, #4]
	LDR      r1, [r4, #0x50]
	CMP      r0, r1
	BNE      |loc_080088A0|
	LDR      r0, [sp, #8]
	LDR      r1, [r4, #0x54]
	CMP      r0, r1
	BEQ      |loc_080088A8|
|loc_080088A0|
	ADD      r1, sp, #4
	ADD      r0, r4, #0
	BL       |loc_08008598|
|loc_080088A8|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_08008192|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080086D8|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080080C0|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_080088DC|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080088E4|
|loc_080088DC|
	LDR      r1, [pc, #0xb4]
	STRB     r4, [r0, #4]
	STR      r1, [r0]
	STR      r5, [r0, #8]
|loc_080088E4|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r3, [pc, #0xac]
	ADD      r4, r0, #0
	ADD      sp, r3
	LDR      r0, [r0, #8]
	ADD      r6, r1, #0
	MOV      r1, sp
	MOV      r5, sp
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDRB     r0, [r4, #4]
	LDR      r1, [pc, #0x9c]
	MOV      r2, #1
	LSL      r0, r0, #0xb
	ADD      r0, r0, r1
	LSL      r2, r2, #0xb
	ADD      r1, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r3, #1
	LSL      r3, r3, #0xb
	ADD      sp, r3
	POP      {r4, r5, r6, pc}
	PUSH     {r4}
	LDR      r2, [r0, #8]
	LDR      r4, [r1, #0x18]
	LDR      r3, [r2, #4]
	SUB      sp, #8
	MUL      r3, r4
	LDR      r4, [r2, #0xc]
	ADD      r3, r3, r4
	LDR      r4, [r1, #0x30]
	ADD      r3, r3, r4
	LDR      r4, [r1, #0x40]
	LDR      r2, [r2, #0x14]
	MUL      r2, r4
	ADD      r2, r3, r2
	STR      r2, [sp]
	LDR      r2, [r0, #8]
	LDR      r4, [r1, #0x1c]
	LDR      r3, [r2, #4]
	MUL      r3, r4
	LDR      r4, [r2, #0x10]
	ADD      r3, r3, r4
	LDR      r4, [r1, #0x34]
	LDR      r1, [r1, #0x40]
	LDR      r2, [r2, #0x18]
	ADD      r3, r3, r4
	MUL      r2, r1
	ADD      r1, r3, r2
	STR      r1, [sp, #4]
	LDRB     r0, [r0, #4]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	LDR      r1, [sp]
	ADD      r0, #0x10
	LDR      r2, [sp, #4]
	ASR      r1, r1, #0xa
	STRH     r1, [r0]
	ASR      r2, r2, #0xa
	STRH     r2, [r0, #2]
	ADD      sp, #8
	POP      {r4}
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08008992|
	LDR      r1, [pc, #8]
	STRB     r4, [r0, #4]
	STR      r1, [r0]
	STR      r5, [r0, #8]
|loc_08008992|
	POP      {r3, r4, r5, pc}
|loc_08008994|
	DCW      0x98b0
	DCW      0x0804,0xf800,0xffff,0xe000
|loc_0800899E|
	LSL      r0, r0, #0x18
