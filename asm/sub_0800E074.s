	CODE16
|sub_0800E074|
	ADD      r2, r1, #0
	ADD      r2, #0x4c
	PUSH     {r4, r5}
	LDRH     r3, [r2]
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0xa1
	STRH     r3, [r2, #0x10]
	ADD      r3, r1, #0
	ADD      r3, #0x4e
	LDRH     r3, [r3]
	STRH     r3, [r2, #0x12]
	ADD      r3, r1, #0
	ADD      r3, #0x50
	LDRH     r3, [r3]
	STRH     r3, [r2, #0x14]
	ADD      r3, r1, #0
	ADD      r3, #0x52
	LDRH     r3, [r3]
	STRH     r3, [r2, #0x16]
	MOV      r3, #0x80
	ADD      r2, #0x10
	STRB     r3, [r2, #8]
	ADD      r4, r1, #0
	ADD      r4, #0x60
	STRB     r3, [r2, #9]
	LDRH     r3, [r4]
	ADD      r2, #0x10
	MOV      r5, #0x5c
	STR      r3, [r2]
	LDRSH    r5, [r5, r1]
	ADD      r3, r4, #7
	STR      r5, [r2, #4]
	LDRB     r3, [r3]
	CMP      r3, #0
	BNE      |loc_0800E0C0|
	MOV      r3, #1
	B        |loc_0800E0C2|
|loc_0800E0C0|
	MOV      r3, #0
|loc_0800E0C2|
	ADD      r1, #0x54
	STR      r3, [r2, #0xc]
	LDRH     r1, [r1]
	LSL      r3, r1, #2
	MOV      r2, #1
	LSL      r2, r2, #9
	ADD      r1, r3, r1
	ADD      r2, r0, r2
	ADD      r1, #0x66
	STR      r1, [r2, #0x38]
	ADD      r1, #0xff
	ADD      r1, #0x41
	STR      r1, [r2, #0x3c]
	MOV      r3, #6
	LDRSB    r1, [r4, r3]
	MOV      r3, #0x29
	LSL      r3, r3, #4
	MUL      r1, r3
	ADD      r0, #0xff
	ADD      r0, #0x81
	STR      r1, [r0, #0x3c]
	POP      {r4, r5}
	BX       lr
|sub_0800E0F0|
|unk_0800E0F0|
		LDR r0, [pc, #0x2a4]
		BX       lr
