	CODE16
|sub_080140B2|
	LDR      r2, [r0, #4]
	ADD      r2, #0xff
	ADD      r2, #1
	LDR      r2, [r2, #0xc]
	LDR      r3, [r0, #8]
	CMP      r2, r3
	BEQ      |loc_080140C4|
	MOV      r0, #0
	BX       lr
|loc_080140C4|
	LDR      r2, [r0, #0x34]
	STR      r2, [r1]
	LDR      r0, [r0, #0x38]
	SUB      r0, #3
	STR      r0, [r1, #4]
	MOV      r0, #1
	BX       lr
|sub_080140D2|
|unk_080140D2|
		PUSH {r4, lr}
		ADD r4, r1, #0
		LDR r1, [r0, #4]
		SUB sp, #8
		ADD r1, #0xff
		ADD r1, #1
		LDR r1, [r1, #0xc]
		LDR r2, [r0, #8]
		CMP r1, r2
		BNE      |sub_080140F6|
		LDR r1, [pc, #0x2c]
		SUB r1, #8
		LDR r1, [r1]
		LDRH r1, [r1, #2]
		LSL r1, r1, #0x1f
		BEQ      |sub_080140F6|
		MOV r2, #1
		B        |inc_0x0158_0x143f2| + 0x13fa0
