	CODE16
|sub_08040E3A|
	MOV      r1, #2
	STRB     r1, [r4, #1]
|loc_08040E3E|
	BL       |loc_08040D4E|
|loc_08040E42|
	LDRB     r0, [r4, #0xb]
	ADD      r1, r5, #0
	ADD      r0, #1
	STRB     r0, [r4, #0xb]
	LDRB     r0, [r4, #3]
	LDRB     r2, [r4]
	CMP      r2, #8
	BEQ      |loc_08040E54|
	MOV      r1, #0
|loc_08040E54|
	LSL      r1, r1, #7
	ORR      r0, r1
	LDRB     r1, [r4, #2]
	LDRB     r2, [r4, #7]
	LSL      r1, r1, #8
	ORR      r0, r1
	ADD      r1, r5, #0
	CMP      r2, #0
	BNE      |loc_08040E68|
	MOV      r1, #0
|loc_08040E68|
	LSL      r1, r1, #0xc
	ORR      r0, r1
	ADD      r3, sp, #0
	LDRH     r1, [r3, #4]
	LSL      r1, r1, #0x1a
	LSR      r1, r1, #0x1e
	CMP      r1, #2
	BCS      |loc_08040E7A|
	MOV      r5, #0
|loc_08040E7A|
	LSL      r1, r5, #0xd
	ORR      r0, r1
	LDRB     r1, [r4, #8]
	ADD      sp, #8
	LSR      r1, r1, #3
	LSL      r1, r1, #0xf
	ORR      r0, r1
	POP      {r4, r5, r6, pc}
	LSL      r0, r0, #0
	LSL      r0, r4, #4
	LSL      r0, r0, #0x10
	LDR      r2, [pc, #0x270]
	LSL      r0, r0, #0xc
	DCW      0xfefe,0x0000
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	LDRB     r0, [r7, #0x1f]
	LSL      r0, r0, #0xc
	LSL      r0, r0, #4
	LSL      r0, r0, #0x10
	LSL      r0, r5, #4
	LSL      r0, r0, #0x10
	STRB     r4, [r6, #0x1b]
	LSR      r3, r7, #1
	LSR      r5, r3, #0xe
	LSR      r4, r0, #0x20
	AND      r3, r0
	LSL      r0, r0, #0
	LSL      r4, r4, #0
	LSL      r0, r0, #0x14
	MOV      r0, #3
	LSL      r0, r0, #0
	STR      r7, [r6, #0x3c]
	LSL      r0, r0, #0
	LSL      r1, r0, #0
	LSL      r0, r0, #0x10
	LSL      r1, r0, #0
	LSL      r0, r0, #0x14
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0xb0]
	MOV      r4, #0
	LDRB     r2, [r5, #0xb]
	LDR      r1, [r5, #0x1c]
	STRB     r2, [r1]
	LDRB     r2, [r5, #2]
	LDRB     r3, [r5, #3]
	EOR      r2, r3
	STRB     r2, [r1, #1]
	MOV      r2, #0
	STRH     r2, [r1, #2]
	LDR      r2, [pc, #0x9c]
	ADD      r1, #4
	SWI      0xb
	LDR      r1, [r5, #0x1c]
	MOV      r0, #0
|loc_08040EEA|
	LSL      r2, r0, #1
	LDRH     r2, [r1, r2]
	ADD      r0, #1
	ADD      r4, r2, r4
	CMP      r0, #4
	BCC      |loc_08040EEA|
	MVN      r0, r4
	SUB      r0, #6
	STRH     r0, [r1, #2]
	MOV      r0, #1
	STRB     r0, [r5, #4]
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x78]
	PUSH     {r4}
	LDRB     r0, [r1]
	MOV      r4, #0
	MOV      r3, #0x80
	CMP      r0, #0
	BEQ      |Irq_WriteMaster3|
	LDRB     r0, [r1, #4]
	CMP      r0, #0
	BEQ      |loc_08040F5A|
	ADD      r0, r1, #0
	LDRB     r1, [r1, #1]
	CMP      r1, #0
	BEQ      |loc_08040F5A|
	LDRB     r1, [r0, #6]
	CMP      r1, #0
	BEQ      |loc_08040F5A|
	MVN      r1, r4
	STR      r1, [r0, #0x18]
	LDR      r1, [r0, #0x28]
	LDR      r2, [r0, #0x24]
	STR      r1, [r0, #0x24]
	STR      r2, [r0, #0x28]
	LDR      r1, [r0, #0x20]
	LDR      r2, [r0, #0x1c]
	STR      r1, [r0, #0x1c]
	STR      r2, [r0, #0x20]
	STRB     r4, [r0, #4]
	LDR      r2, [pc, #0x48]
	STR      r4, [r0, #0x14]
	LDRH     r1, [r2, #8]
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	STRB     r1, [r0, #7]
	LDR      r0, [pc, #0x40]
	ADD      r1, r2, #0
	ADD      r1, #8
	STRH     r0, [r2, #0xa]
	LDRH     r0, [r1]
	ORR      r0, r3
	STRH     r0, [r1]
	LDR      r1, [pc, #0x34]
	MOV      r0, #0xc0
	STRH     r0, [r1, #0xe]
|loc_08040F5A|
	POP      {r4}
	BX       lr
