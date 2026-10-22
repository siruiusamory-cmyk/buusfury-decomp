	CODE16
|sub_08036C4E|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r2, #0
	ADD      r2, r1, #0
	CMP      r1, #0xb
	SUB      sp, #0x1c
	BEQ      |sub_08036CB6|
	CMP      r2, #0xc
	BEQ      |loc_08036CD2|
	MOV      r4, #1
	CMP      r2, #0x21
	LDR      r1, [pc, #0x110]
	BEQ      |loc_08036CE0|
	CMP      r2, #0x22
	BNE      |loc_08036D3E|
	LDR      r2, [r0, #0x10]
	LDR      r3, [r0, #0x14]
	ADD      r2, #0x10
	STR      r2, [sp, #4]
	STR      r2, [sp, #0xc]
	ADD      r3, #0x10
	ADD      r2, #0x20
	STR      r2, [sp, #0x14]
	ADD      r2, r3, #0
	ADD      r2, #0x20
	STR      r2, [sp, #0x18]
	STR      r3, [sp, #8]
	STR      r3, [sp, #0x10]
	LDR      r0, [r0, #0x38]
	ADD      r6, sp, #0xc
	SUB      r0, r0, r1
	BL       |inc_0x049120_0x055620| + 0x9f60
	LDR      r0, [pc, #0xdc]
	LDR      r5, [r0, #4]
	ADD      r5, #0x80
	CMP      r1, #2
	BLT      |loc_08036C9C|
	CMP      r1, #5
	BNE      |loc_08036D44|
|loc_08036C9C|
	MOV      r2, #1
	ADD      r0, r6, #0
	LDR      r1, [r5, #0x28]
	BL       |inc_0x0158_0x143f2| + 0x97d8
	MOV      r2, #1
	ADD      r0, sp, #0xc
	LDR      r1, [r5, #0x30]
	BL       |inc_0x0158_0x143f2| + 0x97d8
	MOV      r0, #0
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
