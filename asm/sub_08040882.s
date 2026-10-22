	CODE16
|sub_08040882|
	LSL      r0, r0, #0xc
	STRH     r7, [r7, #6]
	LSL      r0, r0, #0
|loc_08040888|
	LDR      r0, [pc, #0x88]
	ADD      r6, r0, #0
	LDR      r0, [r0]
	LDRB     r1, [r0, #8]
	LSL      r0, r1, #1
	MOV      r4, sp
	ADD      r2, r0, r4
	ADD      r2, #2
	MOV      r4, #0
	CMP      r4, r1
	BCS      |loc_080408B2|
|loc_0804089E|
	STRH     r3, [r2]
	SUB      r2, #2
	LSR      r3, r3, #1
	ADD      r0, r4, #1
	LSL      r0, r0, #0x18
	LSR      r4, r0, #0x18
	LDR      r0, [r6]
	LDRB     r0, [r0, #8]
	CMP      r4, r0
	BCC      |loc_0804089E|
|loc_080408B2|
	MOV      r0, #1
	STRH     r0, [r2]
	SUB      r2, #2
	STRH     r0, [r2]
	MOV      r4, #0xd0
	LSL      r4, r4, #0x14
	LDR      r0, [pc, #0x54]
	LDR      r0, [r0]
	LDRB     r2, [r0, #8]
	ADD      r2, #3
	MOV      r0, sp
	ADD      r1, r4, #0
	BL       |loc_080407E8|
	ADD      r0, r4, #0
	MOV      r1, sp
	MOV      r2, #0x44
	BL       |loc_080407E8|
	ADD      r2, sp, #8
	ADD      r5, #6
	MOV      r4, #0
	MOV      r6, #1
|loc_080408E0|
	MOV      r1, #0
	MOV      r3, #0
|loc_080408E4|
	LSL      r1, r1, #0x11
	LDRH     r0, [r2]
	AND      r0, r6
	LSR      r1, r1, #0x10
	ORR      r1, r0
	ADD      r2, #2
	ADD      r0, r3, #1
	LSL      r0, r0, #0x18
	LSR      r3, r0, #0x18
	CMP      r3, #0xf
	BLS      |loc_080408E4|
	STRH     r1, [r5]
	SUB      r5, #2
	ADD      r0, r4, #1
	LSL      r0, r0, #0x18
	LSR      r4, r0, #0x18
	CMP      r4, #3
	BLS      |loc_080408E0|
	MOV      r0, #0
|loc_0804090A|
	ADD      sp, #0x88
	POP      {r4, r5, r6}
	POP      {r1}
	BX       r1
	LSL      r0, r0, #0
	STRH     r0, [r7, r3]
	LSL      r0, r0, #0xc
