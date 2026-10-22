	CODE16
|Object_Destroy9|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x134]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x14]
	CMP      r0, #0
	BEQ      |loc_0801639A|
	ADD      r1, r0, #0
	MOV      r0, #1
	STR      r0, [r1, #0xc]
|loc_0801639A|
	LDR      r0, [r4, #0x24]
	BL       |GBARam_Free|
	LDR      r0, [pc, #0x114]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x11c]
	CMP      r1, r0
	BEQ      |loc_080163B4|
	LDR      r0, [pc, #0x10c]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080163B4|
	LDR      r0, [pc, #0x110]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080163C2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080163C2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x18]
	ADD      r1, #1
	ASR      r2, r1, #0x1f
	LSR      r2, r2, #0x1d
	STR      r1, [r0, #0x18]
	ADD      r1, r2, r1
	LDR      r2, [r0, #0x1c]
	ASR      r1, r1, #3
	CMP      r1, r2
	BLT      |loc_080163E4|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xdc]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_080163E4|
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x10]
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #8
	LDR      r2, [r0, #0x38]
	ADD      r2, r2, r0
	MOV      r0, sp
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [sp, #4]
	LDR      r1, [sp]
	LDR      r2, [pc, #0xbc]
	STR      r0, [r4, #0x2c]
	STR      r1, [r4, #0x28]
	ADD      r2, #0x18
	LDR      r3, [r2]
	CMP      r1, r3
	BLT      |sub_08016424|
	LDR      r3, [r2, #8]
	CMP      r1, r3
	BGE      |sub_08016424|
	LDR      r1, [r2, #4]
	CMP      r0, r1
	BLT      |sub_08016424|
	LDR      r1, [r2, #0xc]
	CMP      r0, r1
	BGE      |sub_08016424|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, pc}
