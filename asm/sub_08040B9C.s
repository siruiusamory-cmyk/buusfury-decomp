	CODE16
|sub_08040B9C|
	PUSH     {r4, r5, r6, r7}
	LDR      r0, [pc, #0x2ec]
	SUB      sp, #8
	LDR      r1, [r0, #4]
	LDR      r2, [r0]
	STR      r1, [sp, #4]
	STR      r2, [sp]
	LDRH     r1, [r0, #8]
	LDR      r2, [pc, #0x2e0]
	ADD      r3, sp, #0
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	STRB     r1, [r2, #7]
	LDRH     r1, [r3]
	LDR      r2, [pc, #0x2d8]
	MOV      r6, #0x80
	MOV      r5, #0
	CMP      r1, r2
	BNE      |loc_08040BF8|
	LDR      r1, [pc, #0x2cc]
	LDR      r2, [r1, #0x18]
	CMP      r2, #3
	BLE      |loc_08040BF8|
	MVN      r2, r5
	STR      r2, [r1, #0x18]
	LDR      r2, [r1, #0x28]
	LDR      r3, [r1, #0x24]
	STR      r2, [r1, #0x24]
	STR      r3, [r1, #0x28]
	LDRB     r2, [r1, #4]
	CMP      r2, #0
	BEQ      |loc_08040BE8|
	LDR      r2, [r1, #0x20]
	LDR      r3, [r1, #0x1c]
	STR      r2, [r1, #0x1c]
	STR      r3, [r1, #0x20]
	STRB     r5, [r1, #4]
	STR      r5, [r1, #0x14]
|loc_08040BE8|
	LDR      r2, [pc, #0x2ac]
	STRH     r5, [r2, #8]
	LDR      r3, [pc, #0x2ac]
	LDRH     r1, [r3]
	ORR      r1, r6
	STRH     r1, [r3]
	MOV      r1, #1
	STRH     r1, [r2, #8]
|loc_08040BF8|
	LDR      r4, [pc, #0x294]
	LDR      r1, [r4, #0x14]
	CMP      r1, #3
	BGT      |loc_08040C08|
	LDR      r2, [r4, #0x20]
	LSL      r3, r1, #1
	LDRH     r2, [r2, r3]
	STRH     r2, [r0, #0xa]
|loc_08040C08|
	CMP      r1, #5
	BGE      |loc_08040C10|
	ADD      r1, #1
	STR      r1, [r4, #0x14]
|loc_08040C10|
	LDR      r0, [r4, #0x18]
	CMP      r0, #0
	BLT      |loc_08040C44|
	MOV      r0, #0
	MOV      r7, sp
|loc_08040C1A|
	LSL      r3, r0, #1
	ADD      r3, r3, r0
	LSL      r3, r3, #2
	LSR      r3, r3, #1
	LDR      r2, [r4, #0x24]
	LSL      r3, r3, #1
	ADD      r2, r2, r3
	LDR      r3, [r4, #0x18]
	LSL      r1, r0, #1
	LDRH     r1, [r7, r1]
	LSL      r3, r3, #1
	ADD      r0, #1
	CMP      r0, #2
	STRH     r1, [r2, r3]
	BLT      |loc_08040C1A|
	LDR      r0, [r4, #0x18]
	CMP      r0, #3
	BNE      |loc_08040C44|
	MOV      r1, #1
	STRB     r1, [r4, #5]
	B        |loc_08040C4A|
|loc_08040C44|
	LDR      r0, [r4, #0x18]
	CMP      r0, #5
	BGE      |loc_08040C50|
|loc_08040C4A|
	LDR      r0, [r4, #0x18]
	ADD      r0, #1
	STR      r0, [r4, #0x18]
|loc_08040C50|
	LDRB     r0, [r4]
	LDR      r1, [pc, #0x24c]
	CMP      r0, #0
	BEQ      |loc_08040C5A|
	STRH     r5, [r1, #0xe]
|loc_08040C5A|
	LDR      r2, [r4, #0x14]
	CMP      r2, #5
	BGE      |loc_08040C70|
	CMP      r0, #0
	BEQ      |loc_08040C70|
	LDR      r2, [pc, #0x23c]
	LDRH     r0, [r2]
	ORR      r0, r6
	STRH     r0, [r2]
	MOV      r0, #0xc0
	STRH     r0, [r1, #0xe]
|loc_08040C70|
	STRB     r5, [r4, #9]
	ADD      sp, #8
	POP      {r4, r5, r6, r7}
	BX       lr
