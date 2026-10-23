	CODE16
|sub_08042D72|
	STRB     r1, [r4, #5]
	STRB     r1, [r4, #4]
	MOV      r0, #0x43
	LDRB     r1, [r4, #4]
	CMP      r1, #0
	BNE      |loc_08042CFE|
	BL       |loc_0804333c|
	POP      {r4, r5, r7, pc}
	PUSH     {r7, lr}
	BL       |sub_080440e0|
	CMP      r0, #0
	BEQ      |loc_08042D9A|
	MOV      r1, #0
	MOV      r0, #0xf1
	BL       |loc_0804333c|
	BL       |sub_08043368|
|loc_08042D9A|
	POP      {r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x20c]
	LDRH     r0, [r6, #0x18]
	CMP      r0, #0
	BEQ      |loc_08042E3C|
	LDR      r0, [pc, #0x208]
	LDR      r0, [r0]
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_08042E0A|
	MOV      r6, #0
|loc_08042DB2|
	LDR      r3, [pc, #0x200]
	LSL      r7, r6, #2
	LDR      r0, [r3, r7]
	LDRH     r0, [r0]
	LSL      r0, r0, #0x10
	BPL      |loc_08042E00|
	MOV      r5, #0
	MOV      r4, #0
|loc_08042DC2|
	LDR      r3, [pc, #0x1f0]
	MOV      r1, #1
	LDR      r0, [r3, r7]
	LSL      r1, r4
	LDRB     r0, [r0, #0x1a]
	ADD      r2, r0, #0
	AND      r2, r1
	BEQ      |loc_08042DE6|
	LSL      r2, r4, #2
	LDR      r2, [r3, r2]
	LDR      r3, [pc, #0x1d4]
	LDRH     r2, [r2, #2]
	LDRH     r3, [r3, #0x18]
	CMP      r2, r3
	BLS      |loc_08042DE6|
	ORR      r1, r5
	LSL      r5, r1, #0x18
	LSR      r5, r5, #0x18
|loc_08042DE6|
	CMP      r5, #0
	BEQ      |loc_08042DF6|
	EOR      r0, r5
	ADD      r2, r0, #0
	ADD      r1, r6, #0
	MOV      r0, #0x20
	BL       |inc_0x042118_0x049114| + 0x28f4
|loc_08042DF6|
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	CMP      r4, #4
	BCC      |loc_08042DC2|
|loc_08042E00|
	ADD      r6, #1
	LSL      r6, r6, #0x18
	LSR      r6, r6, #0x18
	CMP      r6, #4
	BCC      |loc_08042DB2|
|loc_08042E0A|
	LDR      r0, [pc, #0x1a4]
	LDR      r0, [r0]
	LDRB     r0, [r0, #5]
	CMP      r0, #0
	BEQ      |loc_08042E3C|
	LDR      r5, [pc, #0x19c]
	LDR      r6, [pc, #0x194]
	MOV      r4, #0
|loc_08042E1A|
	LSL      r0, r4, #2
	LDR      r0, [r5, r0]
	LDRH     r1, [r0, #0x34]
	LSL      r1, r1, #0x10
	BPL      |loc_08042E32|
	LDRH     r0, [r0, #0x36]
	LDRH     r1, [r6, #0x18]
	CMP      r0, r1
	BLS      |loc_08042E32|
	ADD      r0, r4, #0
	BL       |inc_0x042118_0x049114| + 0x29dc
|loc_08042E32|
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	CMP      r4, #4
	BCC      |loc_08042E1A|
|loc_08042E3C|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08042E3E|
	DCW      0x495b
