	CODE16
|sub_080173D6|
	MOV      r1, #0
	STR      r1, [r0, #8]
	MOV      r1, #0xdb
	MOV      r3, #0x70
	MOV      r2, #0x37
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0x5058
	MOV      r3, #0x58
	MOV      r2, #0x50
	MOV      r1, #0x28
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0x4ffc
	MOV      r3, #0xb8
	MOV      r2, #0x50
	MOV      r1, #0x88
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0x4ffc
	LDR      r0, [r7, #8]
	ADD      r3, sp, #0x120
	STR      r0, [sp, #0x134]
	MOV      r0, #0xc
	STRB     r0, [r3, #9]
	LDR      r0, [pc, #0xd4]
	STRB     r5, [r3, #0xa]
	STR      r0, [sp, #0x148]
	STRB     r5, [r3, #8]
	MOV      r5, #0
|loc_08017412|
	LDR      r0, [r4, #0x1c]
	ADD      r6, r0, r5
	LDR      r0, [r4, #0x18]
	CMP      r0, r6
	BLE      |loc_080174BA|
	LSL      r0, r5, #0x1f
	LSR      r0, r0, #0x1f
	LSL      r1, r0, #1
	ADD      r1, r1, r0
	ASR      r0, r5, #1
	MOV      r2, #0x34
	MUL      r2, r0
	LSL      r1, r1, #5
	ADD      r1, #0x40
	ADD      r2, #0x28
	STR      r1, [sp, #0x11c]
	ADD      r1, r6, #0
	STR      r2, [sp, #0x120]
	LDR      r0, [sp, #0x124]
	BL       |inc_0x0158_0x143f2| + 0x1344a
	ADD      r2, sp, #0x11c
	LDMIA    r2!, {r1, r2}
	STR      r1, [sp, #0x12c]
	STR      r2, [sp, #0x130]
	LDR      r2, [r4, #0x20]
	ADD      r7, r0, #0
	MOV      r1, #6
	CMP      r2, r6
	ADD      r0, sp, #0x128
	BEQ      |loc_08017452|
	MOV      r1, #2
|loc_08017452|
	ADD      r3, sp, #0x120
	STRB     r1, [r3, #0xb]
	LDRH     r1, [r7, #0xc]
	LDR      r2, [pc, #0x80]
	ADD      r0, sp, #0x128
	LSL      r1, r1, #2
	LDR      r2, [r2, r1]
	MOV      r1, #0x60
	BL       |inc_0x03d784_0x041118| + 0x5e2
	ADD      r1, sp, #0x12c
	LDMIA    r1!, {r0, r1}
	SUB      r0, #0xc
	STR      r0, [sp, #0x10c]
	ADD      r0, #0x18
	SUB      r1, #8
	STR      r0, [sp, #0x114]
	ADD      r0, r1, #0
	ADD      r0, #0xb
	STR      r0, [sp, #0x118]
	STR      r1, [sp, #0x110]
	ADD      r1, r7, #0
	ADD      r0, sp, #4
	BL       |inc_0x1c3f2_0x2ab4c| + 0xcd46
	ADD      r2, sp, #0x10c
	ADD      r1, sp, #4
	ADD      r0, sp, #0x128
	BL       |inc_0x03d784_0x041118| + 0x219e
	LDRB     r0, [r7]
	CMP      r0, #0xff
	BEQ      |loc_080174B4|
	LDR      r1, [sp, #0x130]
	LDR      r2, [sp, #0x124]
	ADD      r1, #0xc
	STR      r1, [sp, #0x130]
	LSL      r1, r6, #1
	ADD      r1, r1, r2
	ADD      r1, #0x2e
	LDRB     r2, [r1]
	ADD      r0, sp, #0x128
	ADD      r2, #1
	MOV      r1, #0x97
	LDR      r3, [pc, #0x30]
	LSL      r1, r1, #2
	LDR      r1, [r3, r1]
	BL       |inc_0x03d784_0x041118| + 0x512
|loc_080174B4|
	ADD      r5, #1
	CMP      r5, #4
	BLT      |loc_08017412|
|loc_080174BA|
	LDR      r1, [pc, #0x28]
	ADD      r0, sp, #0x128
	BL       |inc_0x049120_0x055620| + 0x30
	MOV      r1, #0
	ADD      r0, sp, #0x128
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x15c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      sp, #0x90
	LSR      r4, r0, #0x20
	STRH     r4, [r7, #0x3e]
	LSR      r3, r5, #1
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	DCW      0xf5a5,0x0803
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	CMP      r2, #8
	BCS      |loc_080175C8|
	ADD      r3, pc, #0x4
	LDRB     r3, [r3, r2]
	LSL      r3, r3, #1
	ADD      pc, r3
|loc_080174F8|
	CMP      r1, #3
	LDR      r3, [r2, #4]
	STR      r7, [r4, #0x74]
|unk_080174FE|
	INCBIN	baserom.gba_0x174fe_0x17500.extracted
	LDR      r0, [pc, #0x190]
	MOV      r6, #0
	LDR      r5, [pc, #0x194]
	LDR      r0, [r0, #4]
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x188]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r4, [r0, #0x14]
	LDR      r5, [r0, #0x20]
	MOV      r0, #0xff
	ADD      r0, #0x25
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08017544|
	LDR      r1, [pc, #0x174]
	LDR      r2, [pc, #0x174]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	STR      r2, [r0]
	ADD      r1, #0x14
	STMIA    r1!, {r4, r5}
|loc_08017544|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	LDR      r0, [pc, #0x144]
	LDR      r4, [pc, #0x14c]
	LDR      r0, [r0, #4]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x13c]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
	LDR      r0, [pc, #0x128]
	LDR      r4, [pc, #0x130]
	LDR      r0, [r0, #4]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x120]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
	LDR      r0, [pc, #0x10c]
	LDR      r4, [pc, #0x114]
	LDR      r0, [r0, #4]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x104]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0xf2
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|sub_080175A0|
|unk_080175A0|
	INCBIN	baserom.gba_0x175a0_0x175c8.extracted
