	CODE16
|sub_080201FE|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x88]
	ADD      r5, r0, #0
	LDR      r1, [r1]
	LDR      r3, [pc, #0x84]
	LDRH     r1, [r1, #4]
	ADD      r5, #0xff
	ADD      r5, #0x2d
	LDR      r3, [r3, #4]
	LDR      r6, [pc, #0x7c]
	LDR      r2, [pc, #0x74]
	ADD      r4, r5, #0
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1f
	SUB      r4, #0x2c
	SUB      r6, #0xc
	ADD      r7, r3, r2
	CMP      r1, #0
	BEQ      |loc_0802024E|
	ADD      r1, r6, #0
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	ADD      r0, r0, r5
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0802024E|
	BL       |inc_0x0158_0x143f2| + 0x4b34
	CMP      r0, #0
	BEQ      |loc_0802024E|
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x1c]
	MOV      r3, #0
	STR      r3, [r4, #0x10]
|loc_0802024E|
	LDR      r0, [pc, #0x3c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_08020282|
	ADD      r1, r6, #0
	MOV      r6, #0
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	LSL      r0, r0, #7
	ADD      r0, r0, r5
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |loc_08020282|
	BL       |inc_0x0158_0x143f2| + 0x4b88
	CMP      r0, #0
	BEQ      |loc_08020282|
	MVN      r0, r6
	STR      r0, [r4, #0x1c]
	STR      r6, [r4, #0x10]
|loc_08020282|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSR      r4, r1, #1
	LSR      r2, r6, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	ADD      r0, r2, r4
	LSL      r0, r0, #0xc
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r3, pc, #0x2F0
	LSR      r4, r0, #0x20
	PUSH     {r4, r6, lr}
	LSR      r4, r0, #0x20
	LSR      r4, r5, #0x1d
	LSL      r0, r0, #0
	LDMIA    r2!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	LSL      r4, r0, #0x16
	LSL      r0, r0, #0
	LSL      r4, r6, #0x17
	LSL      r0, r0, #0
	LSR      r4, r3, #0x1a
	LSL      r0, r0, #0
	LSR      r1, r5, #1
	LSR      r5, r0, #0x20
	LSL      r5, r6, #0x14
	LSR      r5, r0, #0x20
	LSR      r4, r0, #0x1c
	LSL      r0, r0, #0
	PUSH     {r2, r3, r5, r7, lr}
	LSR      r4, r0, #0x20
	MOV      r1, #0xb
	LSL      r1, r1, #6
	ADD      r1, r0, r1
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r1, #0x38]
	CMP      r1, #0
	BEQ      |loc_08020328|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x2d
	ADD      r7, r2, #0
	SUB      r7, #0x2c
	LDR      r6, [r7, #0xc]
	LSL      r1, r6, #7
	LDR      r3, [r2, r1]
	CMP      r3, #0
	BEQ      |loc_08020328|
	ADD      r3, r1, r2
	ADD      r2, r3, #0
	LDR      r4, [r3, #0xc]
	ADD      r2, #0xc
	MOV      r1, #0
	CMP      r4, #0
	BLE      |loc_08020328|
	LDR      r5, [r3, #0x7c]
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #2
	ADD      r3, r3, r2
	LDR      r3, [r3, #0xc]
	CMP      r3, r5
	BNE      |sub_0802032A|
	LDR      r2, [r7, #0x28]
	LSL      r1, r1, #2
	SUB      r2, r6, r2
	LSL      r2, r2, #5
	ADD      r0, r2, r0
	ADD      r0, r0, r1
	MOV      r1, #5
	LSL      r1, r1, #7
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x38]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08020328|
	POP      {r3, r4, r5, r6, r7, pc}
