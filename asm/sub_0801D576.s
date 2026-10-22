	CODE16
|sub_0801D576|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [pc, #0x68]
	LDR      r3, [pc, #0x68]
	LDR      r1, [r1]
	LDR      r5, [pc, #0x68]
	LDRH     r1, [r1, #4]
	LDR      r3, [r3, #4]
	ADD      r4, r0, #0
	LDR      r2, [pc, #0x58]
	ADD      r4, #0xff
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	ADD      r4, #1
	MOV      r7, #0
	SUB      r5, #0xc
	ADD      r6, r3, r2
	CMP      r1, #0
	BEQ      |loc_0801D5B4|
	ADD      r1, r5, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	SUB      r0, #1
	STR      r0, [r4, #0xc]
	BPL      |loc_0801D5B2|
	LDR      r0, [r4, #0x2c]
	STR      r0, [r4, #0xc]
|loc_0801D5B2|
	STR      r7, [r4, #0x10]
|loc_0801D5B4|
	LDR      r0, [pc, #0x2c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801D5DC|
	ADD      r1, r5, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #0xc]
	ADD      r0, #1
	STR      r0, [r4, #0xc]
	LDR      r1, [r4, #0x2c]
	CMP      r0, r1
	BLE      |loc_0801D5DA|
	STR      r7, [r4, #0xc]
|loc_0801D5DA|
	STR      r7, [r4, #0x10]
|loc_0801D5DC|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801D5E0|
	DCW      0x05c4
	DCW      0x0000,0xe9a8
|sub_0801D5E6|
	LSR      r1, r6, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	SUB      r4, r7, r3
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	LDR      r2, [sp, #0x2f0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x35c]
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r1, #0xc]
	MOV      r3, #0x68
	LDRB     r2, [r1]
	ADD      r5, r0, #0
	ADD      r5, #0xff
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r4, r1, r2
	ADD      r5, #1
	LDR      r1, [r5, #0x14]
	LSL      r1, r1, #2
	ADD      r2, r1, r4
	ADD      r2, #0x3c
	LDR      r6, [r2]
	ADD      r1, r5, #0
	ADD      r1, #0x50
	LDR      r0, [r1]
	CMP      r0, #0
	BEQ      |loc_0801D63C|
	ADD      r0, r2, #0
	LDR      r2, [r5, #0x3c]
	LSL      r2, r2, #3
	ADD      r1, r2, r1
	LDR      r1, [r1, #4]
	LSL      r1, r1, #4
	LSR      r1, r1, #4
|loc_0801D634|
	STR      r1, [r0]
	LDR      r2, [r0]
	CMP      r2, r1
	BNE      |loc_0801D634|
|loc_0801D63C|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x13b0e
	LDR      r0, [r5, #0x14]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	ADD      r0, #0x3c
|loc_0801D64A|
	STR      r6, [r0]
	LDR      r1, [r0]
	CMP      r1, r6
	BNE      |loc_0801D64A|
	ADD      r0, r4, #0
	ADD      r0, #0x4c
	LDRH     r0, [r0]
	STR      r0, [r5, #0x28]
	ADD      r0, r4, #0
	ADD      r0, #0x4e
	LDRH     r0, [r0]
	STR      r0, [r5, #0x2c]
	ADD      r0, r4, #0
	ADD      r0, #0x50
	LDRH     r0, [r0]
	STR      r0, [r5, #0x30]
	ADD      r0, r4, #0
	ADD      r0, #0x54
	LDRH     r0, [r0]
	STR      r0, [r5, #0x34]
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	ADD      r5, r0, #0
	CMP      r0, #0
	BNE      |sub_0801D68C|
	LDR      r0, [pc, #0x2dc]
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_0801D68C|
	ADD      r0, r5, #0
	POP      {r3, r4, r5, r6, r7, pc}
