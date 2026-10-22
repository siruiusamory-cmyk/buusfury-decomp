	CODE16
|sub_08010582|
	LSR      r4, r0, #0x20
	BEQ      |loc_080105F8|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x258]
	PUSH     {r4, lr}
	LDR      r0, [r0, #8]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r1, [r0, #0x14]
	LSL      r2, r1, #1
	ADD      r2, r2, r1
	LDR      r1, [pc, #0x244]
	LSL      r2, r2, #3
	ADD      r2, r2, r1
	LDRB     r2, [r2]
	LSL      r2, r2, #0x19
	LSR      r2, r2, #0x1f
	BEQ      |loc_080105D8|
	ADD      r2, r0, #0
	ADD      r2, #0x1e
	MOV      r3, #0
|loc_080105B6|
	STRH     r3, [r2]
	LDRH     r4, [r2]
	CMP      r4, r3
	BNE      |loc_080105B6|
	ADD      r2, r0, #0
	ADD      r2, #0x20
|loc_080105C2|
	STRH     r3, [r2]
	LDRH     r4, [r2]
	CMP      r4, r3
	BNE      |loc_080105C2|
	LDRB     r2, [r0, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LSL      r2, r2, #3
	ADD      r2, r2, r1
	LDRB     r2, [r2, #0x17]
	STRB     r2, [r0, #0x14]
|loc_080105D8|
	LDRB     r0, [r0, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x200]
	LDR      r0, [r0]
	BL       |loc_0800EDF8|
	MOV      r1, #0
	LDR      r0, [pc, #0x1fc]
	BL       |sub_08012588|
|loc_080105F8|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	ADD      r0, r1, #0
	ADD      r5, r1, #0
	LDR      r1, [r1]
	ADD      r4, r2, #0
	LDR      r2, [r1, #0x5c]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_08010618|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_08010618|
	LDR      r0, [r4, #0x18]
	CMP      r0, #0
	BNE      |loc_08010620|
	POP      {r4, r5, r6, pc}
|loc_08010620|
	LDR      r1, [r6]
	ADD      r0, r6, #0
	LDR      r2, [r1, #0xc]
	ADD      r3, r2, r1
	ADD      r2, r4, #0
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r0, r0, r1
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x2c]
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
