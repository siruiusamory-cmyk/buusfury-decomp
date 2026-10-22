	CODE16
|sub_080020D8|
	LDR      r0, [pc, #0x88]
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
	POP      {r3, pc}
	LDR      r1, [pc, #0x98]
	MOV      r0, #1
	STR      r0, [r1, #8]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      sp, #0x14
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	LDR      r7, [pc, #0x64]
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
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x50]
	LDR      r6, [r0, #4]
	LDR      r0, [r1, #8]
	CMP      r0, #0
	BEQ      |loc_08002142|
	LDR      r0, [r7, #0xc]
	BL       |loc_08009196|
	LDR      r1, [pc, #0x40]
	MOV      r0, #0
	STR      r0, [r1, #8]
|loc_08002142|
	MOV      r2, #0
	STR      r2, [sp, #8]
	MOV      r1, #1
	STR      r1, [sp, #4]
	ADD      r0, sp, #0xc
	STR      r0, [sp]
	ADD      r2, r5, #0
	ADD      r3, r4, #0
	ADD      r1, r6, #0
	LDR      r0, [r7, #0xc]
	BL       |loc_08009030|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|loc_0800215E|
	DCW      0x0000
	DCW      0xb2a0,0x0804,0x4fbc,0x0805,0xc7ec,0x0804,0xe0d4,0x0804
	DCW      0xd480,0x0804,0xd494,0x0804,0xe324
|loc_0800217A|
	LSR      r4, r0, #0x20
	BCC      |loc_08002180|
	LSR      r4, r0, #0x20
|loc_08002180|
	ASR      r4, r0, #0x20
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      sp, #0x14
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	MOV      r7, #0
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
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	LDR      r0, [pc, #0x258]
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |loc_080021DA|
	LDR      r0, [pc, #0x254]
	LDR      r0, [r0, #0xc]
	BL       |loc_08009196|
	LDR      r0, [pc, #0x248]
	STR      r7, [r0, #8]
|loc_080021DA|
	MOV      r1, #0x40
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x75f4
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r2, #1
	ADD      r0, sp, #0xc
	STR      r0, [sp]
	STR      r2, [sp, #8]
	MOV      r1, #1
	STR      r1, [sp, #4]
	LDR      r0, [pc, #0x230]
	ADD      r2, r5, #0
	ADD      r3, r4, #0
	ADD      r1, r6, #0
	LDR      r0, [r0, #0xc]
	BL       |loc_08009030|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08002214|
	LDR      r1, [pc, #0x21c]
	STR      r1, [r0]
	MOV      r1, #0x10
	STR      r1, [r0, #8]
	STR      r7, [r0, #4]
|loc_08002214|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
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
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	MOV      r1, #0x40
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x75f4
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [pc, #0x1b4]
	MOV      r7, #0
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |loc_0800227E|
	LDR      r0, [pc, #0x1b0]
	LDR      r0, [r0, #0xc]
	BL       |loc_08009196|
	LDR      r0, [pc, #0x1a4]
	STR      r7, [r0, #8]
|loc_0800227E|
	MOV      r2, #1
	ADD      r0, sp, #0xc
	STR      r0, [sp]
	STR      r2, [sp, #8]
	MOV      r1, #0
	STR      r1, [sp, #4]
	LDR      r0, [pc, #0x198]
	ADD      r2, r5, #0
	ADD      r3, r4, #0
	ADD      r1, r6, #0
	LDR      r0, [r0, #0xc]
	BL       |loc_08009030|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080022AC|
	LDR      r1, [pc, #0x184]
	STR      r1, [r0]
	MOV      r1, #0x10
	STR      r1, [r0, #8]
	STR      r7, [r0, #4]
|loc_080022AC|
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r1, #0x10
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x75f4
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [pc, #0x160]
	LDR      r0, [r0, #0xc]
	BL       |State_CopyBlock1|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080022E0|
	LDR      r1, [pc, #0x150]
	STR      r1, [r0]
	MOV      r1, #0x10
	STR      r1, [r0, #8]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_080022E0|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      sp, #0x10
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	ADD      r3, sp, #0
	STRH     r1, [r3, #0xe]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRH     r1, [r3, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	LDR      r1, [pc, #0x100]
	MOV      r0, #1
	STR      r0, [r1]
	LDR      r0, [pc, #0x100]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08002342|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08002342|
	MOV      r1, #0x40
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x75f4
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r2, #1
	STR      r2, [sp, #4]
	LDR      r0, [pc, #0xd0]
	ADD      r2, r5, #0
	STR      r4, [sp]
	LDR      r0, [r0, #0xc]
	ADD      r1, r6, #0
	ADD      r3, sp, #0xc
	BL       |loc_08008D44|
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800237A|
	LDR      r1, [pc, #0xc4]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #4
	STR      r1, [r0, #8]
|loc_0800237A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      sp, #0x10
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	ADD      r3, sp, #0
	STRH     r1, [r3, #0xe]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRH     r1, [r3, #0xc]
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	LDR      r0, [pc, #0x5c]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_080023E6|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080023E6|
	LDR      r1, [pc, #0x44]
	MOV      r0, #1
	STR      r0, [r1]
	MOV      r2, #0
	STR      r2, [sp, #4]
	LDR      r0, [pc, #0x30]
	ADD      r2, r5, #0
	STR      r4, [sp]
	LDR      r0, [r0, #0xc]
	ADD      r1, r6, #0
	ADD      r3, sp, #0xc
	BL       |loc_08008D44|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x75f4
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, pc}
	LSL      r0, r0, #0
	ASR      r4, r0, #0x20
	LSL      r0, r0, #0xc
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	STMIA    r5!, {r3, r7}
	LSR      r4, r0, #0x20
	CMP      r2, #0x58
	LSL      r0, r0, #0xc
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800245A|
	LDR      r1, [pc, #0x258]
	STR      r1, [r0]
	STR      r4, [r0, #8]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_0800245A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r5, [r0, #4]
	LDR      r0, [pc, #0x240]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0800248E|
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x22ba
	LDR      r0, [pc, #0x234]
	MOV      r1, #0
	STR      r0, [r4]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	ADD      r0, r4, r0
	ADD      r0, #4
	STMIA    r0!, {r1, r5}
|loc_0800248E|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080024B8|
	LDR      r1, [pc, #0x208]
	STR      r1, [r0]
	STR      r4, [r0, #8]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_080024B8|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	CMP      r4, #2
	BGE      |loc_080024D2|
	MOV      r4, #2
|loc_080024D2|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080024E6|
	LDR      r1, [pc, #0x1dc]
	STR      r1, [r0]
	STR      r4, [r0, #8]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_080024E6|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800250E|
	LDR      r1, [pc, #0x1b8]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r4, [r0, #8]
|loc_0800250E|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08002536|
	LDR      r1, [pc, #0x194]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r4, [r0, #8]
|loc_08002536|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [pc, #0x184]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x178]
	SUB      r0, #8
	BL       |inc_0x153f2_0x1a3f2| + 0x2f54
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	LDR      r5, [pc, #0x170]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	LDR      r0, [r5, #0x18]
	BL       |loc_080116FC|
	MOV      r1, #1
	LSL      r1, r1, #0xc
	CMP      r0, r1
	BLT      |loc_080025A2|
	LDR      r0, [r5, #0x28]
	MOV      r1, #0x30
	LDR      r0, [r0]
	SUB      r0, r1, r0
	CMP      r0, #4
	BLT      |loc_080025A2|
	LDR      r0, [r5, #0x18]
	MOV      r1, #0x80
	LDR      r0, [r0, #4]
	SUB      r0, r1, r0
	CMP      r0, #4
	BLT      |loc_080025A2|
	LDR      r2, [pc, #0x138]
	LDR      r3, [pc, #0x138]
	SUB      r2, #8
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |loc_0800D30E|
	ADD      r1, r0, #0
	LDR      r0, [r5, #0x18]
	BL       |List_Append|
|loc_080025A2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	LDR      r5, [pc, #0x120]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	LDR      r0, [r5, #0x18]
	BL       |loc_080116FC|
	MOV      r1, #1
	LSL      r1, r1, #0xc
	CMP      r0, r1
	BLT      |loc_080025F0|
	LDR      r0, [r5, #0x28]
	MOV      r1, #0x30
	LDR      r0, [r0]
	SUB      r0, r1, r0
	CMP      r0, #4
	BLT      |loc_080025F0|
	LDR      r0, [r5, #0x18]
	MOV      r1, #0x80
	LDR      r0, [r0, #4]
	SUB      r0, r1, r0
	CMP      r0, #4
	BLT      |loc_080025F0|
	LDR      r2, [pc, #0xec]
	LDR      r3, [pc, #0xe8]
	SUB      r2, #8
|unk_080025E0|
	INCBIN	baserom.gba_0x25e0_0x25e2.extracted
	MOV      r0, #0
	BL       |loc_0800D30E|
	ADD      r1, r0, #0
	LDR      r0, [r5, #0x18]
	BL       |List_Append|
|loc_080025F0|
	POP      {r3, r4, r5, pc}
	PUSH     {lr}
	LDR      r2, [r0]
	SUB      sp, #0xc
	SUB      r2, #1
	LSL      r1, r2, #2
	STR      r2, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	STR      r2, [sp, #8]
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	LDR      r2, [pc, #0xb0]
	STR      r0, [sp, #4]
	ADD      r0, sp, #4
	ADD      r2, #0x34
	BL       |inc_0x153f2_0x1a3f2| + 0x2f54
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
	LDR      r3, [pc, #0x90]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	ADD      r2, sp, #4
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
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x70]
	ADD      r3, #0x3c
	LDR      r0, [r0, #0xc]
	BL       |loc_080090E6|
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [pc, #0x58]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x50]
	SUB      r2, #8
	LDR      r3, [pc, #0x48]
	LDR      r0, [r0, #0xc]
	BL       |loc_080090E6|
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080026A4|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080026A4|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	LSL      r0, r0, #0
	STMIA    r5!, {r3, r7}
	LSR      r4, r0, #0x20
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
|unk_080026B4|
	INCBIN	baserom.gba_0x26b4_0x26b6.extracted
	LSR      r4, r0, #0x20
	STMIA    r5!, {r3, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r1, sp, #0x360
	LSR      r4, r0, #0x20
	ADR      r5, |loc_08002994|
	LSR      r4, r0, #0x20
	ADR      r0, |loc_08002888|
	LSR      r4, r0, #0x20
	ASR      r0, r3, #0x20
	LSL      r0, r0, #0xc
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	LDR      r1, [sp, #0x1e0]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080026E4|
	LDR      r1, [pc, #0x26c]
	STR      r1, [r0]
|loc_080026E4|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x258]
	LDR      r0, [r0, #0xc]
	BL       |loc_08009172|
	POP      {r3, pc}
	LDR      r0, [pc, #0x250]
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x28]
	ADD      r1, #0xc0
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BEQ      |loc_08002716|
	LDR      r2, [pc, #0x244]
	MOV      r1, #1
	STR      r1, [r2]
|loc_08002716|
	MOV      r1, #0
	LDR      r0, [r0, #0xc]
	BL       |sub_08008AA0|
	POP      {r3, pc}
|sub_08002720|
|unk_08002720|
	INCBIN	baserom.gba_0x2720_0x273a.extracted
