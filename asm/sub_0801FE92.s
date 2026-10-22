	CODE16
|sub_0801FE92|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x11
	LDR      r3, [pc, #0xc4]
	LDRB     r2, [r4, #4]
	LDR      r6, [r3, #4]
	LDR      r1, [pc, #0xb8]
	ADD      r5, r4, #0
	ADD      r7, r6, r1
	MOV      r6, #0
	SUB      r5, #0x10
	CMP      r2, #0
	LDR      r1, [pc, #0xb4]
	BEQ      |sub_0801FEDA|
	CMP      r2, #1
	BNE      |loc_0801FED6|
	ADD      r0, #0xff
	ADD      r0, #0x2d
	LDR      r0, [r0]
	CMP      r0, #0
	BLE      |loc_0801FED6|
	LDR      r0, [r3]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_0801FED6|
	ADD      r3, r6, #0
	MOV      r2, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	STRB     r6, [r4, #4]
	STR      r6, [r5, #0x10]
|loc_0801FED6|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
