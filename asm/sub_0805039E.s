	CODE16
|sub_0805039E|
	LSR      r5, r0, #0x20
	LSL      r5, r6, #0x14
	LSR      r5, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_080503BA|
	MOV      r0, #0xff
	ADD      r0, #0x2d
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080503BA|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080503BA|
	LDR      r0, [pc, #0x44]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #4
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #5
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |sub_0804912C|
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |sub_0804912C|
	LDR      r0, [pc, #0x18]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080503FE|
	DCW      0x0000
	DCW      0x92ec,0x0804,0xffff
|loc_08050406|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	STR      r7, [sp, #0x3d0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_0805042A|
	MOV      r0, #0xff
	ADD      r0, #0x31
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0805042A|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0805042A|
	LDR      r0, [pc, #0x44]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #3
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #4
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |sub_0804912C|
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |sub_0804912C|
	LDR      r0, [pc, #0x18]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	STR      r6, [r5, #0x2c]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08050470|
	DCW      0x92ec
	DCW      0x0804,0xffff
|loc_08050476|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	LDR      r0, [sp, #0x50]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08050496|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0805049A|
|loc_08050496|
	LSL      r1, r4, #8
	STR      r1, [r0]
|loc_0805049A|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_080504AC|
	MOV      r0, #0x80
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080504B0|
|loc_080504AC|
	MOV      r1, #0
	STR      r1, [r0, #0xc]
|loc_080504B0|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	BNE      |loc_080504CA|
	MOV      r0, #0xff
	ADD      r0, #0x31
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080504CA|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080504CA|
	LDR      r0, [pc, #0x44]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #3
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #4
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |sub_0804912C|
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |sub_0804912C|
	LDR      r0, [pc, #0x18]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r6, [r0]
	LDR      r0, [pc, #0x18]
	STR      r0, [r4]
	STR      r6, [r5, #0x2c]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08050510|
	DCW      0x92ec
	DCW      0x0804,0xffff
|loc_08050516|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x1f0]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08050530|
	MOV      r0, #4
	BL       |GBARam_Malloc|
|loc_08050530|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_08050540|
	MOV      r0, #4
	BL       |GBARam_Malloc|
|loc_08050540|
	POP      {r3, pc}
	LSL      r0, r0, #0
