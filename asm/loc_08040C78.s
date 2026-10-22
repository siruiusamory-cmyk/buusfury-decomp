	CODE16
|loc_08040C78|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x21c]
	MOV      r0, #0
	STRH     r0, [r5, #8]
	LDRH     r0, [r5]
	MOV      r1, #0x80
	BIC      r0, r1
	MOV      r1, #0x40
	BIC      r0, r1
	STRH     r0, [r5]
	MOV      r0, #1
	STRH     r0, [r5, #8]
	LDR      r0, [pc, #0x214]
	LDR      r1, [pc, #0x218]
	LDR      r0, [r0]
	MOV      r2, #1
	STR      r1, [r0, #0x18]
	LDR      r0, [pc, #0x20c]
	LDR      r0, [r0]
	STR      r1, [r0, #0x1c]
	LDR      r0, [pc, #0x204]
	LDR      r0, [r0]
	ADD      r0, #0x18
	LDR      r1, [r0]
	ORR      r1, r2
	STR      r1, [r0]
	LDR      r0, [pc, #0x1f8]
	LDR      r0, [r0]
	ADD      r0, #0x1c
	LDR      r1, [r0]
	ORR      r1, r2
	STR      r1, [r0]
	LDR      r0, [pc, #0x1d0]
	MOV      r1, #0
	STRH     r1, [r0, #0x14]
	LSR      r1, r0, #0xd
	STRH     r1, [r0, #8]
	LDR      r2, [pc, #0x1e0]
	LDRH     r0, [r2]
	LDR      r1, [pc, #0x1e8]
	ORR      r0, r1
	STRH     r0, [r2]
	MOV      r0, #0
	STR      r0, [sp]
	LDR      r4, [pc, #0x1bc]
	LDR      r2, [pc, #0x1e0]
	MOV      r0, sp
	ADD      r1, r4, #0
	SWI      0xb
	MOV      r0, #6
	STR      r0, [r4, #0x14]
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	ADD      r0, #0x30
	STR      r0, [r4, #0x1c]
	ADD      r0, r4, #0
	ADD      r0, #0x3c
	STR      r0, [r4, #0x20]
	ADD      r0, r4, #0
	ADD      r0, #0x48
	STR      r0, [r4, #0x24]
	ADD      r0, r4, #0
	ADD      r0, #0x60
	STR      r0, [r4, #0x28]
	ADD      r0, r4, #0
	ADD      r0, #0x78
	STR      r0, [r4, #0x2c]
	MOV      r0, #0
	STRH     r0, [r5, #8]
	LDRH     r0, [r5]
	MOV      r1, #0x80
	ORR      r0, r1
	STRH     r0, [r5]
	MOV      r0, #1
	STRH     r0, [r5, #8]
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x17c]
	LDRB     r0, [r1]
	CMP      r0, #0
	BEQ      |loc_08040D1C|
	MOV      r0, #1
	STRB     r0, [r1, #6]
|loc_08040D1C|
	BX       lr
