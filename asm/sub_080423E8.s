	CODE16
|sub_080423E8|
	ADD      r3, sp, #0
	LDRB     r0, [r3, #8]
	BL       |inc_0x042118_0x049114| + 0x1264
	MOV      r5, #1
	MOV      r1, #2
	MOV      r0, #0x30
|loc_080423F6|
	BL       |loc_0804333c|
	BL       |sub_08043368|
|loc_080423FE|
	LDR      r0, [pc, #0x264]
	LDR      r0, [r0]
	LDRB     r0, [r0]
	CMP      r0, #1
	BNE      |loc_080424AE|
	ADD      r3, sp, #0
	LDRB     r0, [r3]
	CMP      r0, #0
	BEQ      |loc_0804244C|
	MOV      r0, #0
	MOV      r2, #0
|loc_08042414|
	LDRB     r3, [r4]
	ADD      r1, r7, #0
	LSL      r1, r0
	AND      r3, r1
	BEQ      |loc_0804242C|
	ADD      r3, sp, #0
	LDRB     r3, [r3]
	AND      r1, r3
	BEQ      |loc_0804242C|
	LSL      r1, r0, #1
	ADD      r1, r1, r6
	STRH     r2, [r1, #0x34]
|loc_0804242C|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_08042414|
	ADD      r3, sp, #0
	LDRB     r1, [r3]
	LDRB     r0, [r4]
	BIC      r0, r1
	STRB     r0, [r4]
	LDRB     r0, [r3]
	MOV      r1, #1
	STRH     r0, [r6, #0x14]
	MOV      r0, #0x32
	BL       |loc_0804333c|
|loc_0804244C|
	LDRB     r0, [r4]
	CMP      r0, #0
	BEQ      |loc_080424A2|
	MOV      r6, #0
	LDR      r7, [pc, #0x208]
	MOV      r0, #0
|loc_08042458|
	LDRB     r2, [r4]
	MOV      r1, #1
	LSL      r1, r0
	AND      r2, r1
	BEQ      |loc_08042482|
	LSL      r2, r0, #1
	ADD      r3, r2, r7
	LDRH     r2, [r3, #0x34]
	CMP      r2, #0
	BEQ      |loc_08042482|
	SUB      r2, #1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r2, [r3, #0x34]
	BNE      |loc_08042482|
	LDRB     r2, [r4]
	BIC      r2, r1
	ORR      r1, r6
	LSL      r6, r1, #0x18
	LSR      r6, r6, #0x18
	STRB     r2, [r4]
|loc_08042482|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_08042458|
	CMP      r6, #0
	BEQ      |loc_080424A2|
	ADD      r0, r6, #0
	BL       |inc_0x042118_0x049114| + 0x1264
	MOV      r5, #1
	MOV      r1, #1
	MOV      r0, #0x33
	STRH     r6, [r7, #0x14]
	BL       |loc_0804333c|
|loc_080424A2|
	LDRB     r0, [r4]
	LDR      r6, [pc, #0x1b8]
	CMP      r0, #0
	BNE      |loc_080424AE|
	MOV      r2, #0
	STRB     r2, [r6, #0xa]
|loc_080424AE|
	ADD      r0, r5, #0
	POP      {r1, r2, r3, r4, r5, r6, r7, pc}
|unk_080424B2|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x1a8]
	ADD      r4, r1, #0
	LDR      r1, [pc, #0x1a4]
	ADD      r6, r0, #0
	LDRB     r0, [r5, #0xe]
	ADD      r1, #0x30
	SUB      sp, #0x24
	STR      r1, [sp, #0x20]
	CMP      r0, #0
	BEQ      |loc_08042592|
	MOV      r7, #0
	STRB     r7, [r5, #0xe]
	ADD      r0, r5, #0
	LDR      r1, [pc, #0x194]
	LDRB     r0, [r0, #5]
	LDR      r7, [r1]
	CMP      r6, #0x1f
	MOV      ip, r7
	BEQ      |sub_080425B2|
	BGT      |loc_0804251E|
	ADD      r1, r5, #0
	LDRH     r2, [r1, #0x1a]
	ADD      r7, r6, #0
	SUB      r7, #0x10
	SUB      r3, r2, #1
	LSL      r3, r3, #0x10
	LSR      r3, r3, #0x10
	STR      r3, [sp, #0x1c]
	LDRB     r1, [r1, #7]
	CMP      r7, #0xf
	BCS      |loc_080424FC|
	ADD      r3, pc, #0xC
	ADD      r3, r3, r7
	LDRH     r3, [r3, r7]
	LSL      r3, r3, #1
	ADD      pc, r3
|loc_080424FC|
	B        |sub_080425B0|
|sub_080424FE|
|unk_080424FE|
	INCBIN	baserom.gba_0x424fe_0x42500.extracted
|loc_08042500|
|unk_08042500|
	INCBIN	baserom.gba_0x42500_0x4251e.extracted
