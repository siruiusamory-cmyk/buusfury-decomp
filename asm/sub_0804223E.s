	CODE16
|sub_0804223E|
	LSL      r0, r0, #0
	LDR      r4, [pc, #0x320]
	LSL      r0, r0, #0xc
	LDR      r3, [pc, #0x3a0]
	LSL      r0, r0, #0xc
	STRH     r0, [r3, r0]
	LSL      r0, r0, #0xc
	STRH     r4, [r3, r1]
	LSL      r0, r0, #0xc
	STRH     r1, [r3, r0]
	LSL      r0, r0, #0xc
	LDRB     r1, [r7, #0x1f]
	LSL      r0, r0, #0
	STRB     r0, [r1, #0x1c]
	LSR      r3, r7, #1
|loc_0804225C|
	STR      r3, [r2, r1]
|unk_0804225E|
	INCBIN	baserom.gba_0x4225e_0x42260.extracted
	CMP      r0, sb
	STRB     r4, [r2, r1]
	LSL      r1, r1, #1
	LSL      r0, r0, #0
	STRH     r2, [r3, r0]
	LSL      r0, r0, #0xc
	MOV      r0, #0xb1
	LSR      r4, r0, #0x20
	MOV      r0, #0xb9
	LSR      r4, r0, #0x20
	LSL      r0, r0, #4
	LSL      r0, r0, #0x10
	PUSH     {r4, lr}
	BL       |inc_0x042118_0x049114| + 0x18d6
	LDR      r2, [pc, #0x3dc]
	ADD      r4, r0, #0
	CMP      r0, r2
	LDR      r1, [pc, #0x3d8]
	BNE      |loc_0804228C|
	MOV      r0, #1
	STRB     r0, [r1, #8]
|loc_0804228C|
	LDRB     r0, [r1, #4]
	MOV      r2, #0
	CMP      r0, #0x17
	BEQ      |loc_0804229C|
	CMP      r0, #1
	BEQ      |loc_0804229C|
	STRB     r2, [r1, #5]
	STRB     r2, [r1, #4]
|loc_0804229C|
	STRB     r2, [r1, #7]
	STRB     r2, [r1, #0xd]
	STRB     r2, [r1, #1]
	STRB     r2, [r1]
	MOV      r0, #0xff
	STRB     r0, [r1, #6]
	BL       |sub_08043368|
	ADD      r0, r4, #0
	POP      {r4, pc}
	LDR      r1, [pc, #0x3b0]
	PUSH     {r7, lr}
	LDR      r1, [r1]
	LDR      r2, [pc, #0x3a8]
	LDRB     r1, [r1]
	CMP      r1, #0
	BNE      |sub_080422CA|
	LDRB     r0, [r2, #2]
	CMP      r0, #1
	BNE      |sub_080422C6|
	B        |loc_080422CE|
