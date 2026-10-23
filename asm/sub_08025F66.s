	CODE16
|sub_08025F66|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0
	SUB      sp, #0x10
	STR      r0, [sp]
	LDR      r0, [r4, #0x10]
	MOV      r2, sp
	STR      r0, [sp, #4]
	MOV      r0, #0x68
	STR      r0, [sp, #8]
	LDR      r0, [r4, #0x10]
	LDR      r1, [pc, #0x218]
	ADD      r0, #0x38
	STR      r0, [sp, #0xc]
	LDR      r0, [r4, #0x1c]
	BL       |inc_0x049120_0x055620| + 0x3c
	LDR      r1, [r4, #0x24]
	LDR      r2, [r4, #0x10]
	MOV      r0, #1
	CMP      r2, #0
	BGT      |loc_08025F94|
	MOV      r0, #0
|loc_08025F94|
	STR      r0, [r1, #0x20]
	LDR      r0, [r4, #0x28]
	ADD      r4, #0x10
	LDMIA    r4!, {r1, r2}
	CMP      r1, r2
	BGE      |loc_08025FA4|
	MOV      r1, #1
	B        |loc_08025FA6|
|loc_08025FA4|
	MOV      r1, #0
|loc_08025FA6|
	STR      r1, [r0, #0x20]
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x1d8]
	ADD      r4, r0, #0
	LDR      r1, [r5]
	MOV      r0, #0
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	BEQ      |loc_08025FD0|
	LDR      r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |loc_08025FD0|
	SUB      r1, #1
	STR      r1, [r4, #0x10]
	ADD      r0, r4, #0
	BL       |sub_08025F66|
	MOV      r0, #1
|loc_08025FD0|
	LDR      r1, [r5]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_08025FEE|
	LDR      r1, [r4, #0x10]
	LDR      r2, [r4, #0x14]
	CMP      r1, r2
	BGE      |loc_08025FEE|
	ADD      r1, #1
	STR      r1, [r4, #0x10]
	ADD      r0, r4, #0
	BL       |sub_08025F66|
	MOV      r0, #1
|loc_08025FEE|
	LDRB     r1, [r4, #0xd]
	CMP      r1, r0
	BEQ      |loc_08025FF6|
	STRB     r0, [r4, #0xd]
|loc_08025FF6|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |loc_08026004|
	MOV      r0, #1
	STRB     r0, [r4, #0xc]
|loc_08026004|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_08026018|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08026018|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDRB     r1, [r0, #0xc]
	CMP      r1, #0
	BEQ      |sub_08026042|
	MOV      r0, #0x29
	LSL      r0, r0, #5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08026038|
	ADD      r0, r4, #0
	BL       |loc_080261D4|
	LDR      r0, [pc, #0x164]
	STR      r0, [r4]
|loc_08026038|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r4, pc}
|sub_08026042|
|unk_08026042|
	INCBIN	baserom.gba_0x26042_0x26044.extracted
|sub_08026044|
|unk_08026044|
	INCBIN	baserom.gba_0x26044_0x26048.extracted
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x154]
	LDR      r6, [pc, #0x138]
	ADD      r4, r0, #0
	ADD      sp, r3
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x119ac
	LDR      r0, [r4, #0x20]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x11dc8
	LDR      r6, [pc, #0x140]
	ADD      r5, r0, #0
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	ADD      r6, sp
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r0, [pc, #0x110]
	ADD      r3, sp
	LDR      r1, [r3, #0x34]
	ADD      r0, #0x10
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [r4, #0x20]
	LDR      r2, [r4, #0x18]
	ADD      r1, r6, #0
	BL       |sub_08024D94|
	CMP      r5, #0
	BEQ      |loc_080260AC|
	ADD      r7, sp, #0x10
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [pc, #0x10c]
	MOV      r5, sp
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r5!, {r0, r1, r2, r3}
	SUB      r5, #0x10
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
|loc_080260AC|
	LDR      r1, [pc, #0xfc]
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x2234
	LDR      r0, [pc, #0xec]
	MOV      r1, #0
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r0, #0
	LDR      r1, [r4, #0x20]
	BL       |sub_080272EC|
	ADD      r5, r0, #0
	LDR      r6, [pc, #0xbc]
	ADD      r1, r0, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #2
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	MOV      r5, #0
	STR      r5, [r3, #0x34]
	MOV      r0, #0x1e
	STR      r0, [r3, #0x3c]
	STR      r5, [r3, #0x38]
	MOV      r0, #0x14
	STR      r0, [r3, #0x40]
	ADD      r0, r3, #0
	MOV      r2, #1
	ADD      r0, #0x34
	LDR      r1, [pc, #0xb4]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0xac]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	MOV      r0, #0xf
	STR      r0, [r3, #0x34]
	MOV      r0, #0xb
	STR      r0, [r3, #0x38]
	MOV      r0, #0x1c
	STR      r0, [r3, #0x3c]
	MOV      r0, #0x12
	STR      r0, [r3, #0x40]
	MOV      r2, #0x13
	LSL      r2, r2, #5
	ADD      r0, r3, #0
	ADD      r0, #0x34
	LDR      r1, [pc, #0x88]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x84]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	ADD      r1, #0xff
	ADD      r1, #1
	STRH     r1, [r0, #0xe]
	STRH     r5, [r0, #0x18]
	STRH     r5, [r0, #0x1a]
	STRH     r5, [r0, #0x1c]
	MOV      r1, #0x71
	LSL      r1, r1, #6
	STRH     r5, [r0, #0x1e]
	STRH     r1, [r0]
	MOV      r1, #1
	MOV      r0, #0
	BL       |loc_080271D0|
	MOV      r1, #0
	STR      r0, [r4, #0x24]
	MOV      r0, #0
	BL       |loc_080271D0|
	STR      r0, [r4, #0x28]
	LDR      r1, [r4, #0x24]
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [r4, #0x28]
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r4, #0
	BL       |loc_08025F16|
	ADD      r0, r4, #0
	BL       |sub_08025F66|
	LDR      r3, [pc, #0x3c]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
|sub_08026182|
	DCW      0x0000
	DCW      0xa52c,0x0804,0x2374,0x0873,0xd380,0x0874,0xbce8,0x0806
	DCW      0x91f0,0x0804,0x9800,0x0600,0xe3c8,0x0804,0xefbc,0xffff
	DCW      0x1010,0x0000,0x25e8,0x0873,0x0040,0x0600,0xf800
|sub_080261B2|
	LSL      r0, r0, #0x18
	DCW      0xf000,0x0600
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	ASR      r4, r0, #1
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_080261D2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080261D2|
	POP      {r3, pc}
|loc_080261D4|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BNE      |loc_080261EA|
	MOV      r0, #0x29
	LSL      r0, r0, #5
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080261EA|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_080261EA|
	ADD      r0, r4, #0
	BL       |loc_08024A7C|
	LDR      r0, [pc, #0x214]
	ADD      r2, r4, #0
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r4, #0xc]
	LDR      r0, [pc, #0x210]
	MOV      r1, #0x2f
	LDR      r0, [r0, #4]
	LSL      r1, r1, #6
	ADD      r2, #0xc
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x38]
	MOV      r1, #0x16
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08026212|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	MOV      r1, #1
	BL       |loc_08024A9C|
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r7, r5, r1
	MOV      r0, #0
	STR      r0, [r7, #0x18]
	STR      r0, [r7, #0x10]
	LDR      r0, [r5, #0xc]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08026256|
	ADD      r6, r5, #0
	ADD      r6, #0xc
|loc_08026234|
	LSL      r0, r4, #2
	ADD      r0, r0, r4
	LSL      r0, r0, #3
	ADD      r1, r0, r6
	ADD      r1, #4
	MOV      r0, #0
	BL       |loc_08027390|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1c4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r0, [r5, #0xc]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08026234|
|loc_08026256|
	MOV      r0, #0
	BL       |loc_08026F94|
	ADD      r1, r0, #0
	STR      r0, [r7, #0x1c]
	LDR      r0, [pc, #0x1a8]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0x65
	LSL      r0, r0, #6
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1]
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080256F0|
	POP      {r3, pc}
|loc_0802627E|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [r0, #0xc]
	LDR      r5, [pc, #0x18c]
	MOV      r4, #0
	MOV      r2, #0
	CMP      r3, #0
	SUB      sp, #0x14
	MOV      lr, r5
	BLE      |loc_0802630A|
	ADD      r5, r0, #0
	ADD      r5, #0xc
	MOV      ip, r5
|loc_08026296|
	LSL      r3, r2, #2
	ADD      r3, r3, r2
	LSL      r3, r3, #3
	ADD      r3, ip
	ADD      r3, #4
	STR      r3, [sp, #0x10]
	LDR      r5, [r1]
	ADD      r3, #0x14
	LDR      r7, [r3]
	ADD      r6, r3, #0
	CMP      r5, r7
	BLT      |loc_08026302|
	LDR      r7, [r3, #8]
	CMP      r5, r7
	BGE      |loc_08026302|
	LDR      r5, [r1, #4]
	LDR      r7, [r3, #4]
	CMP      r5, r7
	BLT      |loc_08026302|
	LDR      r3, [r3, #0xc]
	CMP      r5, r3
	BGE      |loc_08026302|
	ADD      r3, r6, #0
	LDR      r5, [r6]
	LDR      r7, [r6, #8]
	LDR      r6, [r6, #4]
	ADD      r3, #8
	LDR      r3, [r3, #4]
	ADD      r5, r5, r7
	ADD      r3, r6, r3
	STR      r3, [sp, #4]
	STR      r5, [sp]
	ASR      r5, r5, #1
	ASR      r3, r3, #1
	STR      r3, [sp, #4]
	STR      r3, [sp, #0xc]
	STR      r5, [sp]
	STR      r5, [sp, #8]
	LDR      r3, [r1]
	SUB      r3, r3, r5
	LDR      r5, [r1, #4]
	LDR      r6, [sp, #0xc]
	STR      r3, [sp]
	SUB      r5, r5, r6
	ADD      r6, r3, #0
	MUL      r3, r6
	ADD      r6, r5, #0
	MUL      r6, r5
	ADD      r3, r3, r6
	CMP      r3, lr
	STR      r5, [sp, #4]
	BGE      |loc_08026302|
	LDR      r3, [sp, #0x10]
	LDR      r4, [r3, #0x24]
|loc_08026302|
	LDR      r3, [r0, #0xc]
	ADD      r2, #1
	CMP      r3, r2
	BGT      |loc_08026296|
|loc_0802630A|
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r5, r0, r1
	LDR      r0, [r5, #0x18]
	CMP      r0, r4
	BEQ      |loc_0802632A|
	CMP      r0, #0
	BEQ      |loc_0802631E|
	BL       |loc_08027448|
|loc_0802631E|
	STR      r4, [r5, #0x18]
	CMP      r4, #0
	BEQ      |loc_0802632A|
	ADD      r0, r4, #0
	BL       |sub_08027424|
|loc_0802632A|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	MOV      r1, #5
	LSL      r1, r1, #8
	PUSH     {lr}
	ADD      r1, r0, r1
	LDR      r1, [r1, #0x1c]
	MOV      r2, #0xc1
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	SUB      sp, #0x14
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	ADD      r3, sp, #0xc
	ADD      r1, r3, #0
	STR      r2, [sp, #0x10]
	BL       |loc_0802627E|
	ADD      sp, #0x14
	POP      {pc}
	LDR      r1, [pc, #0xa8]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	LDRH     r1, [r1, #6]
	LSL      r1, r1, #0x1f
	BEQ      |loc_08026388|
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r1, r0, r1
	LDR      r2, [r1, #0x18]
	CMP      r2, #0
	BEQ      |loc_08026388|
	STR      r2, [r1, #0x14]
	MOV      r2, #1
	STR      r2, [r1, #0x10]
	BL       |loc_08024BE6|
	LDR      r0, [pc, #0x90]
	LDR      r1, [pc, #0x90]
	STRH     r0, [r1, #0x10]
|loc_08026388|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r4, r0, r1
	LDR      r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |sub_080263B8|
	LDR      r0, [r4, #0x14]
	BL       |loc_0802745E|
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x14]
	BL       |loc_08027454|
	ADD      r1, r0, #0
	ADD      r2, r5, #0
	MOV      r0, #0
	BL       |loc_08025E50|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
|sub_080263B8|
|unk_080263B8|
	INCBIN	baserom.gba_0x263b8_0x263ba.extracted
|sub_080263BA|
|unk_080263BA|
	INCBIN	baserom.gba_0x263ba_0x263be.extracted
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x1c]
	MOV      r1, #0xc1
	LSL      r1, r1, #4
	ADD      r0, r0, r1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	SUB      sp, #0x10
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	STR      r1, [sp]
	STR      r1, [sp, #8]
	ADD      sp, #0x10
	ASR      r0, r1, #2
	BX       lr
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x1c]
	MOV      r1, #0xc1
	LSL      r1, r1, #4
	ADD      r0, r0, r1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	SUB      sp, #0x10
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      sp, #0x10
	ASR      r0, r0, #2
	BX       lr
|sub_08026406|
	DCW      0x0000
	DCW      0xa570,0x0804,0x25f8,0x0873,0xffff
|sub_08026412|
	LDRB     r7, [r7, #0x1f]
	SUB      r7, #0x5f
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	PUSH     {r4, r5, lr}
	SUB      sp, #0x6c
	MOV      r1, #1
	BL       |loc_08024A9C|
	LDR      r5, [pc, #0x8c]
	LDR      r0, [r5, #4]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	ADD      r1, r4, #0
	LDR      r0, [pc, #0x7c]
	LDR      r2, [r5, #4]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08026448|
	MOV      r2, #1
	LSL      r2, r2, #0xb
	MOV      r1, #0
	LDR      r0, [pc, #0x6c]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #0x1e
	STR      r0, [sp, #0x64]
	MOV      r0, #0x14
	MOV      r4, #0
	STR      r0, [sp, #0x68]
	ADD      r0, sp, #0x5c
	STR      r4, [sp, #0x5c]
	STR      r4, [sp, #0x60]
	MOV      r2, #1
	LDR      r1, [pc, #0x54]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r1, [pc, #0x50]
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	STRH     r1, [r0, #0xc]
	SUB      r1, #0xff
	SUB      r1, #0x44
	STRH     r1, [r0]
	LDR      r1, [pc, #0x48]
	MOV      r0, sp
	MOV      r2, #0
	BL       |inc_0x0158_0x143f2| + 0x3f40
	LDR      r0, [pc, #0x40]
	STRH     r4, [r0]
	STRH     r4, [r0, #2]
	ADD      sp, #0x6c
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080256F0|
	POP      {r3, pc}
	LDR      r1, [pc, #0x18]
	PUSH     {r3, lr}
	SUB      r1, #4
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1f
	BEQ      |loc_080264B0|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_080264B0|
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r6, #4
	LSR      r3, r6, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	DCW      0xf000,0x0600
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	BEQ      |loc_08026448|
	LSR      r7, r6, #1
	LSL      r0, r3, #0
	LSL      r0, r0, #0x10
	LDR      r0, [pc, #0]
	BX       lr
|sub_080264D0|
|unk_080264D0|
	INCBIN	baserom.gba_0x264d0_0x264d2.extracted
|sub_080264D2|
	DCW      0x0300
