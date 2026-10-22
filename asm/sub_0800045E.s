	CODE16
|sub_0800045E|
	LSL      r2, r4, #0x10
	ASR      r2, r2, #0x10
|loc_08000462|
	STRH     r2, [r1]
	MOV      r3, #0
	LDRSH    r4, [r1, r3]
	CMP      r4, r2
	BNE      |loc_08000462|
	LDRB     r1, [r0, #0x13]
	LSL      r1, r1, #0x1f
	BPL      |loc_08000476|
	BL       |loc_08013C66|
|loc_08000476|
	POP      {r3, r4, r5, pc}
	ADD      r2, r0, #0
	LDR      r0, [pc, #0x1ec]
	PUSH     {r3, r4, r5, lr}
	LDR      r0, [r0, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	LSL      r2, r2, #0x10
	ASR      r2, r2, #0x10
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r0, r0, r1
	ADD      r1, r0, #0
	ADD      r1, #0x16
	ADD      r5, r2, #0
|loc_08000498|
	STRH     r2, [r1]
	MOV      r3, #0
	LDRSH    r4, [r1, r3]
	CMP      r4, r2
	BNE      |loc_08000498|
	ADD      r2, r5, #0
|loc_080004A4|
	STRH     r2, [r1, #2]
	MOV      r3, #2
	LDRSH    r4, [r1, r3]
	CMP      r4, r2
	BNE      |loc_080004A4|
	LDRB     r1, [r0, #0x13]
	LSL      r1, r1, #0x1f
	BPL      |loc_080004B8|
	BL       |loc_08013C66|
|loc_080004B8|
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x1ac]
	PUSH     {r4, r5}
	LDR      r1, [r1, #0x14]
	MOV      r3, #0x68
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	LDRB     r2, [r1, #0x14]
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x194]
	LSL      r2, r2, #3
	ADD      r2, r2, r3
	LDRB     r3, [r2]
	LDR      r4, [r0]
	LSL      r2, r3, #0x1e
	LSR      r5, r2, #0x1f
	ADD      r2, r4, #1
	CMP      r5, #0
	BEQ      |sub_080004F8|
	ADD      r1, #0x20
	LDRH     r1, [r1]
	STR      r2, [r0]
	LSL      r2, r4, #2
	ADD      r0, r2, r0
	STR      r1, [r0, #4]
	POP      {r4, r5}
	BX       lr
