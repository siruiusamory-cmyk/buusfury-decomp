	CODE16
|sub_08037F8A|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1e8]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x1f4]
	CMP      r1, r0
	BEQ      |loc_08037FA4|
	LDR      r0, [pc, #0x1dc]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08037FA4|
	LDR      r0, [pc, #0x1e8]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08037FB2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08037FB2|
	POP      {r3, r4, r5, pc}
|sub_08037FB4|
|unk_08037FB4|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDRB r0, [r0, #0x10]
		ADD r6, r4, #0
		LDR r7, [pc, #0x1d4]
		ADD r6, #0x34
		CMP r0, #0
		SUB sp, #0x44
		LDR r5, [r7]
		BEQ      |sub_08038010|
		CMP r0, #1
		BEQ      |sub_080380AA|
		CMP r0, #2
		BNE      |loc_080380A6|
		LDR r0, [r4, #0x2c]
		LDR r1, [r4, #0x30]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		LDR r2, [r4, #0x34]
		SUB r0, r2, r0
		STR r0, [r4, #0x34]
		LDR r0, [r4, #0x38]
		ADD r2, r5, #0
		SUB r0, r0, r1
		STR r0, [r4, #0x38]
		LDR r0, [pc, #0x190]
		ADD r2, #0xff
		ADD r2, #0x9d
		ADD r1, r6, #0
		LDR r0, [r0, #4]
		BL       |loc_080097C2|
		CMP r0, #0
		BEQ      |loc_080380E2|
		LDR r1, [r4, #0x34]
		MOV r0, #0xff
		ADD r0, #0xa1
		LSL r1, r1, #8
		STR r1, [r0, r5]
		LDR r1, [r4, #0x38]
		ADD r0, #4
		LSL r1, r1, #8
		STR r1, [r0, r5]
		B        |sub_080380AA|
