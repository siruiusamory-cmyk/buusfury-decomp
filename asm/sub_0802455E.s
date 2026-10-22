	CODE16
|sub_0802455E|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	LDR      r6, [sp, #0x190]
	LSR      r4, r0, #0x20
	CMP      r7, #0xb0
	LSL      r0, r0, #0xc
	STMIA    r3!, {r3, r7}
	LSR      r2, r6, #1
	PUSH     {r4, r5, r6, lr}
	BL       |loc_08024120|
	MOV      r0, #0xff
	ADD      r0, #0x2d
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_080245C8|
	LDR      r0, [pc, #0x114]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #5
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #6
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0xe8]
	LDR      r1, [pc, #0xec]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0xe4]
	STR      r6, [r0]
	LDR      r0, [pc, #0xe8]
	STR      r6, [r1]
	STR      r0, [r4]
	STR      r6, [r1]
|loc_080245C8|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	LDR      r1, [pc, #0xcc]
	PUSH     {r3, lr}
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |sub_080245FA|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r2, [r1, #0x18]
	ADD      r2, #1
	STR      r2, [r1, #0x18]
	CMP      r2, #0xa
	BLE      |sub_080245FA|
	BL       |inc_0x03d784_0x041118| + 0x29fe
	MOV      r0, #2
	POP      {r3, pc}
