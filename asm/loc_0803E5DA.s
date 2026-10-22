	CODE16
|loc_0803E5DA|
	ADD      r1, r0, #0
	ADD      r1, #0x40
	LDRB     r2, [r1, #8]
	LDRB     r3, [r1, #0xb]
	ADD      r2, r2, r3
	LSL      r2, r2, #0x18
	ASR      r2, r2, #0x18
	STRB     r2, [r1, #8]
	CMP      r2, #0x40
	BLT      |loc_0803E5FA|
	MOV      r2, #0x40
	STRB     r2, [r1, #8]
	LDRB     r2, [r1, #0xa]
	LSR      r2, r2, #2
	LSL      r2, r2, #2
	STRB     r2, [r1, #0xa]
|loc_0803E5FA|
	LDRB     r1, [r1, #8]
	MOV      r2, #0x10
	STRB     r1, [r0, #0x12]
	LDRB     r1, [r0, #0x10]
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	BX       lr
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	MOV      r0, #0x5e
	LDRB     r1, [r0, r4]
	ADD      r0, r4, #0
	ADD      r0, #0x40
	CMP      r1, #0
	BEQ      |loc_0803E61E|
	STRB     r1, [r0, #0xc]
|loc_0803E61E|
	LDRB     r1, [r0, #0xc]
	MOV      r3, #1
	LSL      r2, r1, #0x1c
	LSR      r2, r2, #0x1c
	CMP      r2, #0
	BNE      |loc_0803E646|
	LSR      r1, r1, #4
	STRB     r1, [r0, #0xb]
	LDR      r1, [pc, #0x17c]
	STR      r1, [r4, #0x54]
	LDRB     r1, [r0, #0xa]
	ORR      r1, r3
	STRB     r1, [r0, #0xa]
	LDRB     r0, [r0, #0xb]
	CMP      r0, #0xf
	BNE      |loc_0803E644|
	ADD      r0, r4, #0
	BL       |loc_0803E5DA|
|loc_0803E644|
	POP      {r4, r5, pc}
|loc_0803E646|
	LSL      r2, r1, #0x18
	LSR      r5, r2, #0x1c
	BNE      |loc_0803E668|
	LDRB     r1, [r0, #0xc]
	STRB     r1, [r0, #0xb]
	LDR      r1, [pc, #0x15c]
	STR      r1, [r4, #0x54]
	LDRB     r1, [r0, #0xa]
	ORR      r1, r3
	STRB     r1, [r0, #0xa]
	LDRB     r0, [r0, #0xb]
	CMP      r0, #0xf
	BNE      |loc_0803E644|
	ADD      r0, r4, #0
	BL       |loc_0803E5AC|
	POP      {r4, r5, pc}
|loc_0803E668|
	MOV      r3, #0xf
	BIC      r3, r1
	BNE      |loc_0803E67A|
	LSR      r1, r1, #4
	STRB     r1, [r0, #0xb]
	ADD      r0, r4, #0
	BL       |loc_0803E5DA|
|loc_0803E678|
	POP      {r4, r5, pc}
|loc_0803E67A|
	LSR      r2, r2, #0x1c
	CMP      r2, #0xf
	BNE      |loc_0803E678|
	AND      r1, r2
	STRB     r1, [r0, #0xb]
	ADD      r0, r4, #0
	BL       |loc_0803E5AC|
	POP      {r4, r5, pc}
	MOV      r1, #0x4d
	LDRB     r1, [r1, r0]
	LDR      r3, [pc, #0x120]
	LDR      r2, [r0, #0x40]
	LSL      r1, r1, #1
	LDRH     r1, [r3, r1]
	MUL      r2, r1
	LSR      r1, r2, #0x10
	STR      r1, [r0, #0x40]
	STR      r1, [r0, #0x30]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	BX       lr
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	MOV      r0, #0x5e
	LDRB     r1, [r0, r4]
	ADD      r0, r4, #0
	ADD      r0, #0x40
	CMP      r1, #0
	BEQ      |loc_0803E6C0|
	STRB     r1, [r0, #0xd]
|loc_0803E6C0|
	LDRB     r3, [r0, #0xa]
	LSL      r1, r3, #0x1d
	LSR      r1, r1, #0x1f
	BEQ      |loc_0803E6EC|
	LDRB     r1, [r0, #0xd]
	MOV      r5, #2
	LSL      r2, r1, #0x18
	LSR      r2, r2, #0x1c
	CMP      r2, #0xf
	BNE      |loc_0803E6EE|
	LSL      r0, r1, #0x1c
	LDR      r2, [pc, #0xdc]
	LSR      r0, r0, #0x1b
	LDRH     r0, [r2, r0]
	LDR      r1, [r4, #0x40]
	MUL      r1, r0
	LSR      r0, r1, #0x10
	STR      r0, [r4, #0x40]
	STR      r0, [r4, #0x30]
	LDRB     r0, [r4, #0x10]
	ORR      r0, r5
	STRB     r0, [r4, #0x10]
|loc_0803E6EC|
	POP      {r4, r5, pc}
|loc_0803E6EE|
	CMP      r2, #0xe
	BNE      |loc_0803E70E|
	LDR      r2, [pc, #0xc0]
	LSL      r0, r1, #0x1c
	LSR      r0, r0, #0x1b
	SUB      r2, #0x80
	LDRH     r0, [r2, r0]
	LDR      r1, [r4, #0x40]
	MUL      r1, r0
	LSR      r0, r1, #0x10
	STR      r0, [r4, #0x40]
	STR      r0, [r4, #0x30]
	LDRB     r0, [r4, #0x10]
	ORR      r0, r5
	STRB     r0, [r4, #0x10]
	POP      {r4, r5, pc}
|loc_0803E70E|
	LDR      r1, [pc, #0xa8]
	STR      r1, [r4, #0x54]
	MOV      r1, #1
	ORR      r1, r3
	STRB     r1, [r0, #0xa]
	POP      {r4, r5, pc}
	MOV      r1, #0x4d
	LDRB     r1, [r1, r0]
	LDR      r3, [pc, #0x9c]
	LDR      r2, [r0, #0x40]
	LSL      r1, r1, #1
	LDRH     r1, [r3, r1]
	MUL      r2, r1
	LSR      r1, r2, #0xe
	STR      r1, [r0, #0x40]
	STR      r1, [r0, #0x30]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #2
	ORR      r1, r2
	STRB     r1, [r0, #0x10]
	BX       lr
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	MOV      r0, #0x5e
	LDRB     r1, [r0, r4]
	ADD      r0, r4, #0
	ADD      r0, #0x40
	CMP      r1, #0
	BEQ      |loc_0803E74E|
	STRB     r1, [r0, #0xd]
|loc_0803E74E|
	LDRB     r3, [r0, #0xa]
	LSL      r1, r3, #0x1d
	LSR      r1, r1, #0x1f
	BEQ      |loc_0803E77A|
	LDRB     r1, [r0, #0xd]
	MOV      r5, #2
	LSL      r2, r1, #0x18
	LSR      r2, r2, #0x1c
	CMP      r2, #0xf
	BNE      |loc_0803E77C|
	LSL      r0, r1, #0x1c
	LDR      r2, [pc, #0x54]
	LSR      r0, r0, #0x1b
	LDRH     r0, [r2, r0]
	LDR      r1, [r4, #0x40]
	MUL      r1, r0
	LSR      r0, r1, #0xe
	STR      r0, [r4, #0x40]
	STR      r0, [r4, #0x30]
	LDRB     r0, [r4, #0x10]
	ORR      r0, r5
	STRB     r0, [r4, #0x10]
|loc_0803E77A|
	POP      {r4, r5, pc}
|loc_0803E77C|
	CMP      r2, #0xe
	BNE      |loc_0803E79C|
	LDR      r2, [pc, #0x38]
	LSL      r0, r1, #0x1c
	LSR      r0, r0, #0x1b
	SUB      r2, #0x80
	LDRH     r0, [r2, r0]
	LDR      r1, [r4, #0x40]
	MUL      r1, r0
	LSR      r0, r1, #0xf
	STR      r0, [r4, #0x40]
	STR      r0, [r4, #0x30]
	LDRB     r0, [r4, #0x10]
	ORR      r0, r5
	STRB     r0, [r4, #0x10]
	POP      {r4, r5, pc}
|loc_0803E79C|
	LDR      r1, [pc, #0x20]
	STR      r1, [r4, #0x54]
	MOV      r1, #1
	ORR      r1, r3
	STRB     r1, [r0, #0xa]
	POP      {r4, r5, pc}
|loc_0803E7A8|
	DCW      0x6724
	DCW      0x087b,0xe5db,0x0803,0xe5ad,0x0803,0x6c84,0x087b,0xe68d
	DCW      0x0803,0x6a04,0x087b,0xe71b
|loc_0803E7C2|
	LSR      r3, r0, #0x20
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r4, r5}
	LDRB     r2, [r1, #0xd]
	LDR      r4, [pc, #0x278]
	LDR      r3, [r0, #0x40]
	LSL      r2, r2, #1
	LDRH     r2, [r4, r2]
	MOV      r5, #2
	MUL      r3, r2
	LSR      r4, r3, #0x10
	STR      r4, [r0, #0x40]
	STR      r4, [r0, #0x30]
	LDRB     r2, [r0, #0x10]
	ORR      r2, r5
	ADD      r3, r2, #0
	STRB     r3, [r0, #0x10]
	LDR      r2, [r0, #0x44]
	CMP      r4, r2
	BCS      |loc_0803E802|
	STR      r2, [r0, #0x40]
	STR      r2, [r0, #0x30]
	ORR      r3, r5
	ADD      r2, r3, #0
	STRB     r2, [r0, #0x10]
	LDRB     r0, [r1, #0xa]
	MOV      r2, #8
	BIC      r0, r2
	LSR      r0, r0, #2
	LSL      r0, r0, #2
	STRB     r0, [r1, #0xa]
|loc_0803E802|
	POP      {r4, r5}
	BX       lr
	ADD      r1, r0, #0
	ADD      r1, #0x40
	PUSH     {r4, r5}
	LDRB     r2, [r1, #0xd]
	LDR      r4, [pc, #0x23c]
	LDR      r3, [r0, #0x40]
	LSL      r2, r2, #1
	LDRH     r2, [r4, r2]
	MOV      r5, #2
	MUL      r3, r2
	LSR      r4, r3, #0xe
	STR      r4, [r0, #0x40]
	STR      r4, [r0, #0x30]
	LDRB     r2, [r0, #0x10]
	ORR      r2, r5
	ADD      r3, r2, #0
	STRB     r3, [r0, #0x10]
	LDR      r2, [r0, #0x44]
	CMP      r4, r2
	BLS      |loc_0803E844|
	STR      r2, [r0, #0x40]
	STR      r2, [r0, #0x30]
	ORR      r3, r5
	ADD      r2, r3, #0
	STRB     r2, [r0, #0x10]
	LDRB     r0, [r1, #0xa]
	MOV      r2, #8
	BIC      r0, r2
	LSR      r0, r0, #2
	LSL      r0, r0, #2
	STRB     r0, [r1, #0xa]
|loc_0803E844|
	POP      {r4, r5}
	BX       lr
|sub_0803E848|
|unk_0803E848|
	INCBIN	baserom.gba_0x3e848_0x3e89a.extracted
