	CODE16
|sub_080271AE|
	LSL      r0, r0, #0
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BEQ      |loc_08027230|
	LSR      r4, r6, #1
	BPL      |loc_08027184|
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LSR      r0, r3, #0x10
	LSL      r0, r0, #0
	LSR      r4, r3, #0x10
	LSL      r0, r0, #0
	LSR      r4, r2, #0x10
	LSL      r0, r0, #0
	MOV      r0, #0
	STRH     r0, [r0]
|loc_080271D0|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_080271E8|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080271E8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080271E8|
	LDR      r0, [pc, #0xb0]
	LDR      r6, [pc, #0xb4]
	STR      r0, [r4]
	MOV      r0, #0x40
	STRH     r0, [r4, #0xe]
	LDR      r0, [r6]
	MOV      r1, #0x40
	BL       |inc_0x0158_0x143f2| + 0x110f4
	ADD      r3, r0, #1
	BNE      |loc_0802720E|
	MOV      r1, #0x40
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	MOV      r1, #0x40
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x110f4
|loc_0802720E|
	STRH     r0, [r4, #0xc]
	LDR      r0, [pc, #0x90]
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r4, #0x14]
	STRB     r5, [r4, #0x1c]
	MOV      r0, #1
	STR      r0, [r4, #0x20]
	LDR      r0, [pc, #0x80]
	ADD      r0, #0x94
	CMP      r5, #2
	BGE      |loc_08027228|
	SUB      r0, #0x80
|loc_08027228|
	STR      r0, [r4, #0x10]
	MOV      r0, #0
	MVN      r0, r0
	STR      r0, [r4, #0x18]
|loc_08027230|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|sub_08027234|
|unk_08027234|
		PUSH {r3, lr}
		ADD r1, r0, #0
		LDR r0, [r0, #0x20]
		CMP r0, #0
		BEQ      |sub_0802724A|
		LDR r0, [r1, #0x14]
		ADD r0, #1
		STR r0, [r1, #0x14]
		LSL r0, r0, #0x1b
		LSR r2, r0, #0x1f
		DCW     0xE001
