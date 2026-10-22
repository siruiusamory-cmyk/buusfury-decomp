	CODE16
|sub_08042BF8|
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [pc, #0x3b0]
	ADD      r4, r0, #0
	LDRB     r0, [r5, #4]
	ADD      r6, r1, #0
	CMP      r0, #0
	BEQ      |loc_08042C1E|
	CMP      r0, #9
	BCC      |loc_08042C0E|
	CMP      r0, #0xb
	BLS      |loc_08042C1E|
|loc_08042C0E|
	MOV      r0, #1
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_08042C1E|
	BL       |loc_0804400c|
	CMP      r0, #0
	BNE      |sub_08042C36|
	MOV      r0, #2
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #2
	POP      {r4, r5, r6, pc}
