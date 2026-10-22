	CODE16
|sub_0805012E|
	LSL      r0, r0, #0
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0805013E|
	MOV      r0, #0
|loc_0805013E|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, #0x20
	LSL      r0, r0, #0xc
	MOV      r0, #1
	BX       lr
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0805015A|
	MOV      r0, #0
|loc_0805015A|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	SUB      r0, r7, r4
	LSL      r0, r0, #0xc
	MOV      r0, #1
	LSL      r2, r0, #9
	ADD      r1, r1, r2
	LDR      r1, [r1, #4]
	CMP      r1, #0
	BNE      |loc_08050172|
	MOV      r0, #0
|loc_08050172|
	BX       lr
|sub_08050174|
|unk_08050174|
		MOV r0, #1
		BX       lr
