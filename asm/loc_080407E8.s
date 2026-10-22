	CODE16
|loc_080407E8|
	PUSH     {r4, r5, r6, lr}
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	LDR      r4, [pc, #0x58]
	LDRH     r3, [r4]
	ADD      r6, r3, #0
	MOV      r3, #0
	STRH     r3, [r4]
	LDR      r5, [pc, #0x50]
	LDRH     r4, [r5]
	LDR      r3, [pc, #0x50]
	AND      r4, r3
	LDR      r3, [pc, #0x50]
	LDR      r3, [r3]
	LDRH     r3, [r3, #6]
	ORR      r4, r3
	STRH     r4, [r5]
	LDR      r3, [pc, #0x4c]
	STR      r0, [r3]
	LDR      r0, [pc, #0x4c]
	STR      r1, [r0]
	LDR      r1, [pc, #0x4c]
	MOV      r0, #0x80
	LSL      r0, r0, #0x18
	ORR      r2, r0
	STR      r2, [r1]
	ADD      r1, #2
	MOV      r2, #0x80
	LSL      r2, r2, #8
	ADD      r0, r2, #0
	LDRH     r1, [r1]
	AND      r0, r1
	CMP      r0, #0
	BEQ      |loc_0804083C|
	LDR      r2, [pc, #0x34]
	MOV      r0, #0x80
	LSL      r0, r0, #8
	ADD      r1, r0, #0
|loc_08040834|
	LDRH     r0, [r2]
	AND      r0, r1
	CMP      r0, #0
	BNE      |loc_08040834|
|loc_0804083C|
	LDR      r0, [pc, #8]
	STRH     r6, [r0]
	POP      {r4, r5, r6}
	POP      {r0}
	BX       r0
|loc_08040846|
	DCW      0x0000
	DCW      0x0208,0x0400,0x0204,0x0400,0xf8ff,0x0000,0x52f8,0x0300
	DCW      0x00d4,0x0400,0x00d8,0x0400,0x00dc,0x0400,0x00de,0x0400
