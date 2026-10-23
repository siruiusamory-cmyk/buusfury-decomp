	CODE16
|sub_0804E608|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r0, #0xec
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	MOV      r2, #0
	STR      r2, [r3, #4]
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0xe
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r4, r4
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r4, r4
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r0, #0xd0
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |dat_08034280| + 0x28
	LDR      r1, [r5]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4, #0xc]
	MUL      r1, r0
	ASR      r0, r1, #0x10
	STR      r0, [r4, #0x10]
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0xc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #0x14]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x15
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r4, r4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x64]
	SUB      sp, #0x24
	ADD      r7, r1, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r5, #1
|loc_0804E724|
	LSL      r5, r5, #0xa
	CMP      r0, r5
	BLT      |loc_0804E776|
	LSL      r4, r5, #2
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r4, r0, r4
	ADD      r0, sp, #0xc
	ADD      r1, r7, #0
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	LDR      r2, [sp, #0x18]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp, #4]
	STR      r0, [sp, #8]
	MOV      r2, #0x37
	STR      r1, [sp, #0x1c]
	STR      r0, [sp, #0x20]
	ADD      r7, sp, #0x1c
	ADD      r1, r7, #0
	STR      r2, [sp, #8]
	MOV      r3, #4
	MOV      r0, #0
	LDR      r2, [pc, #0x18]
	STR      r4, [sp]
	STR      r5, [sp, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0804E776|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	STR      r3, [sp, #0x180]
	LSR      r5, r6, #1
	BLS      |loc_0804E724|
	LSR      r7, r5, #1
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r2, #0xc
	MOV      r1, #0
	ADD      r0, #4
	BL       |sub_08049168|
	MOV      r0, #0
	STR      r0, [r4, #0x10]
	STR      r0, [r4, #0x14]
	POP      {r4, pc}
	LSL      r0, r0, #0
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0x64
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x15
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r1, #0x28
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	MOV      r0, #0
	STRH     r0, [r1, #0x16]
	MOV      r1, #0x15
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r4, r4
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #4
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0x14
	LSL      r0, r0, #0xc
	ADD      r0, #4
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	STR      r1, [r0]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0xe
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0x54
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xf7cc
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0xa0
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r7, r4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x64]
	SUB      sp, #0x24
	ADD      r7, r1, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r5, #1
|loc_0804E8A4|
	LSL      r5, r5, #0xa
	CMP      r0, r5
	BLT      |loc_0804E8F6|
	LSL      r4, r5, #2
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r4, r0, r4
	ADD      r0, sp, #0xc
	ADD      r1, r7, #0
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	LDR      r2, [sp, #0x18]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp, #4]
	STR      r0, [sp, #8]
	MOV      r2, #0x37
	STR      r1, [sp, #0x1c]
	STR      r0, [sp, #0x20]
	ADD      r7, sp, #0x1c
	ADD      r1, r7, #0
	STR      r2, [sp, #8]
	MOV      r3, #4
	MOV      r0, #0
	LDR      r2, [pc, #0x18]
	STR      r4, [sp]
	STR      r5, [sp, #4]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_0804E8F6|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	STR      r3, [sp, #0x80]
	LSR      r5, r6, #1
	BLS      |loc_0804E8A4|
	LSR      r7, r5, #1
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0xe
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0x54
	LSL      r0, r0, #0xc
	MOV      r3, #0
	STRH     r3, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	STR      r3, [r0, #4]
	BX       lr
	PUSH     {r3, lr}
	MOV      r2, #0
	STR      r2, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0xdd08
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xf7cc
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
|sub_0804E954|
|unk_0804E954|
	INCBIN	baserom.gba_0x4e954_0x4e956.extracted
|sub_0804E956|
	DCW      0x0300
