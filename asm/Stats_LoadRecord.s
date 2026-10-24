	CODE16
|Stats_LoadRecord|
	PUSH     {r4, r5}
	LDRH     r2, [r1, #2]
	LSL      r2, r2, #0x10
	ASR      r2, r2, #0x10
	ADD      r5, r2, #0
|loc_080133A6|
	STRH     r2, [r0, #0x16]
	MOV      r3, #0x16
	LDRSH    r4, [r0, r3]
	CMP      r4, r2
	BNE      |loc_080133A6|
	ADD      r2, r5, #0
|loc_080133B2|
	STRH     r2, [r0, #0x18]
	MOV      r3, #0x18
	LDRSH    r4, [r0, r3]
	CMP      r4, r2
	BNE      |loc_080133B2|
	LDRH     r2, [r1, #4]
	LSL      r2, r2, #0x10
	ASR      r2, r2, #0x10
	ADD      r5, r2, #0
|loc_080133C4|
	STRH     r2, [r0, #0x1a]
	MOV      r3, #0x1a
	LDRSH    r4, [r0, r3]
	CMP      r4, r2
	BNE      |loc_080133C4|
	ADD      r2, r5, #0
|loc_080133D0|
	STRH     r2, [r0, #0x1c]
	MOV      r3, #0x1c
	LDRSH    r4, [r0, r3]
	CMP      r4, r2
	BNE      |loc_080133D0|
	LDRB     r3, [r1, #6]
	ADD      r2, r0, #0
	ADD      r2, #0x28
|loc_080133E0|
	STRB     r3, [r2]
	LDRB     r4, [r2]
	CMP      r4, r3
	BNE      |loc_080133E0|
	LDRB     r3, [r1, #7]
	ADD      r2, r0, #0
	ADD      r2, #0x29
|loc_080133EE|
	STRB     r3, [r2]
	LDRB     r4, [r2]
	CMP      r4, r3
	BNE      |loc_080133EE|
	LDRB     r3, [r1, #8]
	ADD      r2, r0, #0
	ADD      r2, #0x2a
|loc_080133FC|
	STRB     r3, [r2]
	LDRB     r4, [r2]
	CMP      r4, r3
	BNE      |loc_080133FC|
	LDRB     r3, [r1, #9]
	ADD      r2, r0, #0
	ADD      r2, #0x2b
|loc_0801340A|
	STRB     r3, [r2]
	LDRB     r4, [r2]
	CMP      r4, r3
	BNE      |loc_0801340A|
	LDRB     r2, [r1]
	CMP      r2, #0x32
	BGE      |sub_0801341C|
	MOV      r2, #0
	B        |loc_08013436|
