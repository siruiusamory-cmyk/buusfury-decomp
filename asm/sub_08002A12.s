	CODE16
|sub_08002A12|
	MOV      r1, #0
	ADD      r3, r2, #1
	STR      r3, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	STR      r1, [r0, #4]
	POP      {r4, r5}
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x1b4]
	LDR      r0, [r0, #0x14]
	BL       |loc_08004544|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	LDR      r4, [pc, #0x1a4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	LDR      r0, [r4, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MOV      r5, #0x9f
	LSL      r5, r5, #3
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	LDRB     r0, [r0, #0x14]
	LDR      r7, [pc, #0x198]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r7
	BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
	LDR      r0, [r4, #0x14]
	MOV      r2, #0x13
	LSL      r2, r2, #6
	STRB     r6, [r0]
	ADD      r0, r0, r2
	MOV      r1, #0
	STR      r1, [r0, #0x1c]
	LDR      r0, [pc, #0x174]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08002A9A|
	LDR      r1, [r4, #0x14]
	MOV      r3, #0x68
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	ADD      r1, r1, r5
	BL       |loc_08010692|
|loc_08002A9A|
	LDR      r0, [r4, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	LDRB     r0, [r0, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r7
	BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	LDR      r2, [r0]
	MOV      r3, #0x68
	SUB      r2, #1
	LSL      r1, r2, #2
	STR      r2, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r2, [r0, #4]
	LDR      r0, [pc, #0x11c]
	MUL      r2, r3
	LDR      r0, [r0, #0x14]
	ADD      r0, r2, r0
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r0, r0, r2
	BL       |sub_08013A90|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r2, [r0]
	MOV      r3, #0x68
	SUB      r2, #1
	LSL      r1, r2, #2
	STR      r2, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r2, [r0, #4]
	LDR      r0, [pc, #0xf0]
	MUL      r2, r3
	LDR      r0, [r0, #0x14]
	ADD      r0, r2, r0
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r0, r0, r2
	BL       |loc_08013ABA|
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r3, [r0]
	SUB      r3, #1
	LSL      r1, r3, #2
	STR      r3, [r0]
	ADD      r1, r1, r0
	LDR      r2, [r1, #4]
	SUB      r3, #1
	LSL      r1, r3, #2
	STR      r3, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r3, #1
	STR      r3, [r0]
	LSL      r3, r3, #2
	ADD      r0, r3, r0
	LDR      r4, [r0, #4]
	MOV      r3, #0x68
	LDR      r0, [pc, #0xb8]
	MUL      r3, r4
	LDR      r0, [r0, #0x14]
	ADD      r0, r3, r0
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r0, r0, r3
	BL       |loc_08013B12|
	POP      {r4, pc}
	PUSH     {r4}
	LDR      r1, [r0]
	MOV      r3, #0x68
	SUB      r1, #1
	LSL      r2, r1, #2
	ADD      r2, r2, r0
	STR      r1, [r0]
	LDR      r4, [r2, #4]
	LDR      r2, [pc, #0x94]
	MUL      r3, r4
	LDR      r2, [r2, #0x14]
	ADD      r2, r3, r2
	MOV      r3, #0x9f
	LSL      r3, r3, #3
	ADD      r2, r2, r3
	LDRB     r2, [r2]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r2, r2, #0x1f
	LSR      r2, r2, #0x1f
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	LDR      r1, [pc, #0x70]
	LDR      r2, [r0]
	LDR      r1, [r1, #0x14]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	MOV      r3, #0x68
	MUL      r0, r3
	ADD      r0, r0, r1
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r1, [r0]
	MOV      r2, #1
	ORR      r1, r2
	STRB     r1, [r0]
	BX       lr
	LDR      r1, [pc, #0x4c]
	LDR      r2, [r0]
	LDR      r1, [r1, #0x14]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	MOV      r3, #0x68
	MUL      r0, r3
	ADD      r0, r0, r1
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r1, [r0]
	LSR      r1, r1, #1
	LSL      r1, r1, #1
	STRB     r1, [r0]
	BX       lr
	LDR      r1, [pc, #0x24]
	LDR      r2, [r0]
	LDR      r1, [r1, #0x14]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	MOV      r3, #0x68
	MUL      r0, r3
	ADD      r0, r0, r1
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r1, [r0]
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	LDMIA    r0!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LDR      r1, [pc, #0x2a4]
	LDR      r2, [r0]
	LDR      r1, [r1, #0x14]
	SUB      r2, #1
	STR      r2, [r0]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #4]
	MOV      r3, #0x68
	MUL      r0, r3
	ADD      r0, r0, r1
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	LDRB     r1, [r0]
	MOV      r2, #2
	BIC      r1, r2
	STRB     r1, [r0]
	BX       lr
|sub_08002C2A|
|unk_08002C2A|
; cited by 0x08002954 (a pc-relative load targets 0x08002C48)
	INCBIN	baserom.gba_0x2c2a_0x2c58.extracted
