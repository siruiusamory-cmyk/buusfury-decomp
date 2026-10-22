	CODE16
|sub_08013D84|
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
|loc_08013D88|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_08013D88|
	LDRH     r1, [r4, #4]
	MOV      r0, #0x58
	STRH     r1, [r0, r5]
	LDRH     r1, [r4, #6]
	MOV      r0, #0x5a
	STRH     r1, [r0, r5]
	LDRH     r1, [r4, #8]
	MOV      r0, #0x5c
	STRH     r1, [r0, r5]
	LDRH     r1, [r4, #0xa]
	MOV      r0, #0x5e
	STRH     r1, [r0, r5]
	LDRH     r1, [r4, #0xc]
	ADD      r0, r5, #0
	ADD      r0, #0x60
	STRH     r1, [r0]
	LDRB     r2, [r4, #1]
	MOV      r1, #0x56
	STRB     r2, [r1, r5]
	LDRB     r2, [r4, #2]
	MOV      r1, #0x57
	STRB     r2, [r1, r5]
	LDRH     r2, [r4, #0xe]
	MOV      r1, #0x62
	STRH     r2, [r1, r5]
	LDRH     r2, [r4, #0x10]
	MOV      r1, #0x64
	STRH     r2, [r1, r5]
	LDRB     r1, [r4]
	STRB     r1, [r0, #6]
	LDR      r1, [sp]
	MOV      r0, #0x67
	LDRB     r1, [r1]
	STRB     r1, [r0, r5]
	POP      {r3, r4, r5, r6, r7, pc}
