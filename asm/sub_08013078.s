	CODE16
|sub_08013078|
|unk_08013078|
		LDR r0, [r5, #4]
		MOV r1, #1
		ADD r0, #1
		LSL r1, r1, #0xa
		CMP r0, r1
		STR r0, [r5, #4]
		BLE      |loc_080130A6|
		LDR r0, [r4, #0x58]
		LDRB r1, [r0]
		CMP r1, #8
		BLS      |loc_080130A4|
		LDR r0, [r0, #0x74]
		CMP r0, #0
		BEQ      |loc_080130A4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #8
		BL       |loc_08046AA4|
		B        |loc_080130A6|
|loc_080130A4|
		STR r6, [r5, #4]
|loc_080130A6|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		MOV r1, #0xf0
		AND r0, r1
		BEQ      |loc_080130F6|
		LDR r1, [pc, #0x27c]
		MOV r2, #1
		LSL r2, r2, #9
		ADD r2, r4, r2
		LDR r1, [r1, #4]
		LDR r3, [r2, #0x34]
		SUB r5, r1, r3
		MOV r3, #0x11
		LSL r3, r3, #5
		ADD r3, r7, r3
		CMP r5, #0x14
		BHS      |loc_080130F2|
		NEG r5, r0
		ADD r7, r0, #0
		BIC r7, r5
		BNE      |loc_080130F2|
		LDRH r5, [r3, #0x10]
		AND r5, r0
		BEQ      |loc_080130F2|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #2
		BL       |loc_08046AA4|
|loc_080130F0|
		B        |inc_0x0158_0x143f2| + 0x12f1e
|loc_080130F2|
		STRH r0, [r3, #0x10]
		STR r1, [r2, #0x34]
|loc_080130F6|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #2]
		MOV r5, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1c
		BEQ      |loc_08013180|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1a
		LSR r0, r0, #0x1f
		BEQ      |loc_08013128|
		MOV r0, #2
		STRB r0, [r4, #0x10]
|loc_08013128|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_08013142|
		MOV r0, #3
		STRB r0, [r4, #0x10]
|loc_08013142|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x19
		LSR r0, r0, #0x1f
		BEQ      |loc_0801315A|
		STRB r5, [r4, #0x10]
|loc_0801315A|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_08013172|
		STRB r6, [r4, #0x10]
|loc_08013172|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_08013180|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1f
		BEQ      |loc_0801319C|
		ADD r0, r4, #0
		BL       |sub_08012A24|
		B        |inc_0x0158_0x143f2| + 0x12f1e
|loc_0801319C|
		LDR r1, [r4]
		MOV r2, #0x84
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |loc_080130F0|
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x131b4_0x131b6.extracted
|sub_080131B6|
|unk_080131B6|
	INCBIN	baserom.gba_0x131b6_0x131ba.extracted
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x84
	LDR      r2, [r2, r1]
	SUB      sp, #0xc
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x17
	LSR      r0, r0, #0x1f
	BEQ      |sub_08013210|
	LDR      r0, [r4, #0x58]
	LDRB     r1, [r0]
	CMP      r1, #7
	BLS      |sub_08013210|
	LDR      r0, [r0, #0x70]
	CMP      r0, #0
	BEQ      |sub_08013210|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080131FA|
	LDR      r1, [pc, #0x144]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #4]
|loc_080131FA|
	ADD      r4, r0, #0
	MOV      r1, #7
	ADD      r0, r7, #0
	BL       |Record_SelectIndexed|
	ADD      r1, r4, #0
	ADD      r0, r7, #0
	BL       |loc_0800ED18|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
