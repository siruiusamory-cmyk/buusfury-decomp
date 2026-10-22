	CODE16
|sub_0803F0E6|
	MOV      r1, #0
	MOV      r2, #0
	PUSH     {r4}
|loc_0803F0EC|
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #5
	ADD      r3, r3, r0
	ADD      r3, #0x18
	MOV      r4, #0x4a
	STRB     r2, [r4, r3]
	ADD      r4, r3, #0
	ADD      r4, #0x50
	STRB     r2, [r4, #0xf]
	STRB     r2, [r4, #8]
	STRB     r2, [r3, #0x10]
	ADD      r1, #1
	CMP      r1, #0xf
	STR      r3, [r3, #0x2c]
	BLT      |loc_0803F0EC|
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6, lr}
	MOV      r5, #1
	STRB     r5, [r0, #2]
	STRB     r5, [r0]
	MOV      r2, #0
	STRB     r2, [r0, #1]
	STR      r1, [r0, #0xc]
	ADD      r4, r0, #0
	LDRB     r0, [r1, #0x11]
	STRB     r0, [r4, #3]
	MVN      r0, r2
	STR      r0, [r4, #0x10]
	MOV      r0, #0
|loc_0803F12A|
	LSL      r3, r0, #1
	ADD      r3, r3, r0
	LSL      r3, r3, #5
	ADD      r3, r3, r4
	ADD      r3, #0x18
	MOV      r6, #0x4a
	STRB     r2, [r6, r3]
	ADD      r6, r3, #0
	ADD      r6, #0x50
	STRB     r2, [r6, #0xf]
	STRB     r2, [r6, #8]
	STRB     r2, [r3, #0x10]
	ADD      r0, #1
	CMP      r0, #0xf
	STR      r3, [r3, #0x2c]
	BLT      |loc_0803F12A|
	LDRB     r0, [r1, #0x10]
	LDR      r1, [pc, #0x64]
	STRB     r0, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0xd40
	STRH     r0, [r4, #6]
	STRB     r5, [r4, #5]
	POP      {r4, r5, r6, pc}
	MOV      r1, #0
	MOV      r2, #0
	PUSH     {r4}
|loc_0803F160|
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #5
	ADD      r3, r3, r0
	ADD      r3, #0x18
	MOV      r4, #0x4a
	STRB     r2, [r4, r3]
	ADD      r4, r3, #0
	ADD      r4, #0x50
	STRB     r2, [r4, #0xf]
	STRB     r2, [r4, #8]
	STRB     r2, [r3, #0x10]
	ADD      r1, #1
	CMP      r1, #0xf
	STR      r3, [r3, #0x2c]
	BLT      |loc_0803F160|
	LDRB     r1, [r0, #2]
	STRB     r1, [r0, #1]
	MOV      r1, #1
	STRB     r1, [r0]
	POP      {r4}
	BX       lr
