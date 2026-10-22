	CODE16
|loc_0800E3E6|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	BL       |loc_0800E1D0|
	LDR      r0, [r4, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x18]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0800E46E|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0xa
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800E46E|
	LDR      r1, [pc, #0x21c]
	LDR      r0, [r5, #0x14]
	ADD      r0, r0, r1
	STR      r0, [r5, #0x14]
	LSR      r0, r0, #0x10
	BEQ      |loc_0800E46E|
	LDR      r1, [r4]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r0, #0
	ADD      r1, #0x1e
	LDRH     r2, [r1]
	CMP      r2, #0
	BEQ      |loc_0800E44E|
	ADD      r0, r1, #0
	LDRH     r1, [r1]
	LDRH     r1, [r0]
	MOV      r2, #1
	SUB      r1, r1, r2
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
|loc_0800E444|
	STRH     r1, [r0]
	LDRH     r2, [r0]
	CMP      r2, r1
	BNE      |loc_0800E444|
	B        |loc_0800E466|
|loc_0800E44E|
	ADD      r0, #0x16
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	CMP      r0, #0
	BEQ      |loc_0800E466|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0x18
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800E466|
	LDR      r0, [r5, #0x14]
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STR      r0, [r5, #0x14]
|loc_0800E46E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	BL       |loc_08013C66|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_0800E074|
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDRH     r1, [r0, #0x10]
	ADD      r1, #0xf
	STRH     r1, [r0, #0x10]
	LDRH     r1, [r0, #0x12]
	ADD      r1, #0xf
	STRH     r1, [r0, #0x12]
	LDRH     r1, [r0, #0x14]
	ADD      r1, #0xf
	STRH     r1, [r0, #0x14]
	LDRH     r1, [r0, #0x16]
	ADD      r1, #0xf
	STRH     r1, [r0, #0x16]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r1, [r0, #0x38]
	ADD      r1, #0xc0
	STR      r1, [r0, #0x38]
	LDR      r1, [r0, #0x3c]
	ADD      r1, #0xc0
	STR      r1, [r0, #0x3c]
	POP      {r3, r4, r5, pc}
|sub_0800E4C2|
|unk_0800E4C2|
		B        |loc_0800E1D0|
