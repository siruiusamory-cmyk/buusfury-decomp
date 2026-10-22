	CODE16
|sub_0801342C|
	LSL      r2, r2, #2
	ADD      r2, r2, r3
	SUB      r2, #0xff
	SUB      r2, #1
	LDR      r2, [r2, #0x38]
|loc_08013436|
	STR      r2, [r0, #0x24]
	LDR      r3, [r0, #0x24]
	CMP      r3, r2
	BNE      |loc_08013436|
	MOV      r2, #2
	STRB     r2, [r0]
	LDRB     r2, [r1, #0xa]
	STRB     r2, [r0, #0x14]
	MOV      r2, #0
	MVN      r2, r2
	STR      r2, [r0, #8]
	MOV      r2, #0
|loc_0801344E|
	STR      r2, [r0, #0x3c]
	LDR      r3, [r0, #0x3c]
	CMP      r3, r2
	BNE      |loc_0801344E|
	MOV      r2, #0x2c
|loc_08013458|
	STR      r2, [r0, #0x40]
	LDR      r3, [r0, #0x40]
	CMP      r3, r2
	BNE      |loc_08013458|
	MOV      r2, #0x4d
|loc_08013462|
	STR      r2, [r0, #0x44]
	LDR      r3, [r0, #0x44]
	CMP      r3, r2
	BNE      |loc_08013462|
	MOV      r2, #0x70
|loc_0801346C|
	STR      r2, [r0, #0x48]
	LDR      r3, [r0, #0x48]
	CMP      r3, r2
	BNE      |loc_0801346C|
	LDRB     r3, [r1, #0xb]
	MOV      r2, #0
	CMP      r3, #0
	STRB     r3, [r0, #0xc]
	BLE      |loc_0801348E|
|loc_0801347E|
	ADD      r3, r1, r2
	LDRB     r3, [r3, #0xc]
	ADD      r4, r0, r2
	ADD      r2, #1
	STRB     r3, [r4, #0xd]
	LDRB     r3, [r0, #0xc]
	CMP      r3, r2
	BGT      |loc_0801347E|
|loc_0801348E|
	POP      {r4, r5}
	BX       lr
	LDRB     r1, [r0, #0x14]
	LDR      r2, [pc, #0x17c]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1]
	LSL      r2, r1, #0x1e
	LSR      r2, r2, #0x1f
	BEQ      |loc_080134AA|
	LDRH     r0, [r0, #0x20]
	BX       lr
|loc_080134AA|
	LSL      r1, r1, #0x1f
	BEQ      |loc_080134B2|
	LDRH     r0, [r0, #0x1e]
	BX       lr
|loc_080134B2|
	MOV      r3, #0x1a
	LDRSH    r0, [r0, r3]
	BX       lr
	MOV      r2, #0x56
	LDRB     r2, [r2, r0]
	MUL      r2, r1
	ASR      r1, r2, #4
	LDRB     r2, [r0, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x14c]
	LSL      r2, r2, #3
	ADD      r2, r2, r3
	LDRB     r2, [r2]
	LSL      r3, r2, #0x1e
	LSR      r3, r3, #0x1f
	BEQ      |sub_080134E2|
	LDRH     r0, [r0, #0x20]
	CMP      r0, r1
	BLT      |sub_080134DE|
	MOV      r0, #1
	BX       lr
