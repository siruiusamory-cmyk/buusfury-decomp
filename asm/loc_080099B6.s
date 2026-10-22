	CODE16
|loc_080099B6|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r0, #0xc4
	SUB      sp, #8
	BL       |GBARam_Malloc|
	ADD      r5, r6, #0
	ADD      r5, #0x80
	ADD      r4, r0, #0
	CMP      r0, #0
	BEQ      |loc_08009A00|
	MOV      r2, #0x5c
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0xcb8
	LDR      r2, [pc, #0x104]
	ADD      r1, r6, #0
	ADD      r1, #0x5c
	ADD      r0, r4, #0
	STR      r2, [sp]
	ADD      r2, r1, #0
	ADD      r0, #0x5c
	MOV      r3, #0xc
	ADD      r2, #0x30
	BL       |inc_0x046118_0x049114| + 0xf00
	LDR      r0, [r5, #0xc]
	MOV      r1, #0x8c
	STR      r0, [r1, r4]
	ADD      r1, r6, #0
	ADD      r1, #0x90
	ADD      r0, r4, #0
	MOV      r2, #0x34
	ADD      r0, #0x90
	BL       |inc_0x046118_0x049114| + 0xcb8
|loc_08009A00|
	LDR      r0, [pc, #0xdc]
	STR      r4, [r0]
	MOV      r0, #1
	LSL      r0, r0, #0xd
	BL       |GBARam_Malloc|
	STR      r0, [r5, #0x28]
	MOV      r0, #1
	LSL      r0, r0, #0xd
	BL       |GBARam_Malloc|
	STR      r0, [r5, #0x2c]
	MOV      r0, #1
	LSL      r0, r0, #0xd
	BL       |GBARam_Malloc|
	STR      r0, [r5, #0x30]
	MOV      r0, #0
	STR      r0, [r5, #0x10]
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
