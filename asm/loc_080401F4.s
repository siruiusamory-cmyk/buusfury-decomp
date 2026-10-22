	CODE16
|loc_080401F4|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x2c]
	ADD      r5, r4, #4
	LDMIA    r5!, {r0, r5}
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x18]
	LDR      r0, [r0, #0x14]
	STR      r0, [r4, #0xc]
	STR      r5, [r4, #4]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
|loc_0804021C|
	DCW      0x76f0
	DCW      0x087b,0x4a6c,0x0300,0x0ff0,0x0300,0x9618,0x0804,0xb868
	DCW      0x0804,0xb254,0x0804,0x9644,0x0804,0xffff
|loc_0804023A|
	LSL      r0, r0, #0
	PUSH     {r4}
	LDRH     r4, [r0, #2]
	ADD      r3, r1, #0
	ADD      r2, r4, #0
	EOR      r2, r1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	AND      r3, r2
	AND      r4, r2
	STRH     r3, [r0, #4]
	STRH     r4, [r0, #6]
	STRH     r1, [r0, #2]
	CMP      r3, #0
	BEQ      |loc_08040280|
	LDRB     r1, [r0]
	LSL      r1, r1, #1
	ADD      r1, r1, r0
	STRH     r3, [r1, #8]
	LDRB     r2, [r0]
	LDR      r1, [pc, #0xf4]
	LSL      r2, r2, #2
	ADD      r2, r2, r0
	LDR      r1, [r1, #4]
	ADD      r2, #0x80
	STR      r1, [r2, #8]
	LDRB     r1, [r0]
	ADD      r1, #1
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	STRB     r1, [r0]
	CMP      r1, #0x40
	BCC      |loc_08040280|
	MOV      r1, #0
	STRB     r1, [r0]
|loc_08040280|
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6}
	LDRH     r4, [r0, #4]
	CMP      r4, #0
	BNE      |sub_08040292|
	MOV      r0, #0
	POP      {r4, r5, r6}
	BX       lr
