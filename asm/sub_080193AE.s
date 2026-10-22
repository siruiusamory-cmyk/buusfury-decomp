	CODE16
|sub_080193AE|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	CMP      r1, #0xc
	BEQ      |loc_080193D8|
	CMP      r1, #0xd
	BEQ      |loc_0801942A|
	CMP      r1, #0xe
	BNE      |sub_08019440|
	LDR      r0, [r4]
	CMP      r0, #0
	BEQ      |loc_080193D0|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080193D0|
	MOV      r0, #0
	STR      r0, [r4]
	MOV      r0, #1
	POP      {r4, pc}
|loc_080193D8|
	LDR      r0, [r4]
	CMP      r0, #0
	BNE      |loc_080193E2|
	MOV      r0, #1
	POP      {r4, pc}
|loc_080193E2|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_08019426|
	LDR      r0, [r4]
	LDR      r1, [r0, #4]
	CMP      r1, #0
	BNE      |loc_0801941A|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0801941A|
	MOV      r0, #1
	POP      {r4, pc}
|loc_0801941A|
	LDR      r0, [pc, #0x54]
	LDR      r1, [r4]
	LDR      r0, [r0]
	ADD      r2, r4, #0
	BL       |sub_08019444|
|loc_08019426|
	MOV      r0, #2
	POP      {r4, pc}
|loc_0801942A|
	LDR      r0, [r4]
	CMP      r0, #0
	BEQ      |loc_0801943C|
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801943C|
	MOV      r0, #1
	POP      {r4, pc}
