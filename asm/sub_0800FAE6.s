	CODE16
|sub_0800FAE6|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0800EF08|
	MOV      r0, #0x47
	LSL      r0, r0, #3
	ADD      r0, r4, r0
	BL       |loc_0800AB0C|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	ADD      r7, r2, #4
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	CMP      r1, #0
	SUB      sp, #0x7c
	BEQ      |loc_0800FBE0|
	CMP      r6, #2
	BEQ      |loc_0800FBE2|
	LDR      r7, [pc, #0x1cc]
	CMP      r6, #0x16
	BEQ      |sub_0800FB56|
	CMP      r6, #0x19
	BNE      |loc_0800FBE4|
	ADD      r1, r4, #0
	ADD      r6, sp, #0x6c
	ADD      r0, r6, #0
	BL       |loc_0800FE78|
	LDR      r0, [r7, #8]
	LDR      r1, [sp, #0x6c]
	ADD      r0, #0x18
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |loc_0800FC16|
	LDR      r1, [r0]
	LDR      r2, [sp, #0x74]
	CMP      r1, r2
	BGE      |loc_0800FC16|
	LDR      r1, [sp, #0x70]
	LDR      r2, [r0, #0xc]
	CMP      r1, r2
	BGE      |loc_0800FC16|
	LDR      r0, [r0, #4]
	LDR      r1, [sp, #0x78]
	CMP      r0, r1
	BGE      |loc_0800FC16|
	LDR      r0, [r5]
	CMP      r0, #0x10
	BNE      |loc_0800FC36|
	MOV      r0, #0
	ADD      sp, #0x7c
	POP      {r4, r5, r6, r7, pc}
