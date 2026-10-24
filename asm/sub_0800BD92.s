	CODE16
|sub_0800BD92|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |Handle_Acquire1|
	MOV      r0, #0xff
	STRB     r0, [r4, #0x1c]
	POP      {r4, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x30]
	MOV      r2, #0x80
	LDR      r1, [r0]
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	LDR      r6, [pc, #0xb8]
	LDR      r0, [r4, #0x2c]
	SUB      r6, #0x18
	CMP      r0, #0
	BNE      |loc_0800BDEA|
	LDR      r0, [r5, #8]
	CMP      r0, #0
	BLT      |loc_0800BDEA|
	LDRB     r0, [r5, #0x14]
	LDR      r1, [pc, #0xbc]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1c
	LSR      r0, r0, #0x1f
	BEQ      |loc_0800BDEA|
	ADD      r1, r4, #0
	MOV      r0, #0
	BL       |sub_0800B5F0|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x2c]
	LDR      r0, [r6, #8]
	BL       |List_Append|
|loc_0800BDEA|
	LDR      r0, [r4, #0x30]
	MOV      r2, #0x84
	LDR      r1, [r0]
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x1f
	BEQ      |loc_0800BE1A|
	ADD      r0, r5, #0
	BL       |sub_08013B34|
	CMP      r0, #0
	BEQ      |loc_0800BE1A|
	LDR      r5, [pc, #0x80]
	LDR      r0, [r6, #4]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x70]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0800BE1A|
	LDR      r0, [r4, #0x34]
	MOV      r2, #0x80
	LDR      r1, [r0]
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	LDR      r0, [r4, #0x34]
	MOV      r2, #0x84
	LDR      r1, [r0]
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x1f
	BEQ      |loc_0800BE46|
	ADD      r0, r5, #0
	BL       |sub_08013B34|
|loc_0800BE46|
	ADD      r0, r4, #0
	BL       |loc_0800B8FC|
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x30]
	ADD      r5, r1, #0
	LDR      r1, [r0]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r2, r0, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |Gfx_BuildVitalBars|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
|sub_0800BE70|
|unk_0800BE70|
	INCBIN	baserom.gba_0xbe70_0xbe72.extracted
