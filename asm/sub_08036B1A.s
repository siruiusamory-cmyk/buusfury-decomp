	CODE16
|sub_08036B1A|
	MOV      r0, #0x5a
	STR      r0, [r4, #0x34]
	LDR      r0, [pc, #0x25c]
	LDR      r5, [r0]
	CMP      r5, #0
	BEQ      |loc_08036B98|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r5]
	CMP      r0, #0
	BEQ      |loc_08036B98|
	LDR      r0, [r4, #0x38]
	SUB      r0, r0, r6
	CMP      r0, #0x18
	BLT      |loc_08036B98|
	CMP      r0, #0x3c
	BGE      |loc_08036B98|
	LDR      r0, [r4, #0x10]
	LDR      r1, [r4, #0x14]
	ADD      r0, #0x10
	STR      r0, [sp, #0xc]
	STR      r0, [sp, #0x18]
	ADD      r1, #0x10
	ADD      r0, #0x20
	STR      r0, [sp, #0x20]
	ADD      r0, r1, #0
	ADD      r0, #0x20
	STR      r0, [sp, #0x24]
	STR      r1, [sp, #0x10]
	STR      r1, [sp, #0x1c]
	ADD      r1, r5, #0
	ADD      r0, sp, #4
	ADD      r6, sp, #0x28
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #4]
	LDR      r1, [sp, #0x20]
	CMP      r0, r1
	BGE      |loc_08036B98|
	LDR      r0, [sp, #0x18]
	LDR      r1, [sp, #0xc]
	CMP      r0, r1
	BGE      |loc_08036B98|
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x24]
	CMP      r0, r1
	BGE      |loc_08036B98|
	LDR      r0, [sp, #0x1c]
	LDR      r1, [sp, #0x10]
	CMP      r0, r1
	BGE      |loc_08036B98|
	MOV      r0, #1
	LSL      r0, r0, #0xa
	STR      r0, [sp, #0x40]
	MOV      r0, #0
	STR      r0, [sp, #0x38]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x5c]
	ADD      r2, r2, r1
	ADD      r1, r6, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08036B98|
	ADD      sp, #0x48
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5}
	LDR      r2, [pc, #0x1d4]
	LDR      r1, [r0, #0x38]
	ADD      r2, #0x18
	CMP      r1, r2
	SUB      sp, #8
	BNE      |sub_08036BB2|
	MOV      r0, #0
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
