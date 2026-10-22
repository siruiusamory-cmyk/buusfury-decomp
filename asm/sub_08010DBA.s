	CODE16
|sub_08010DBA|
|unk_08010DBA|
		LDR r0, [pc, #0x178]
		MOV r1, #0x2f
		SUB r0, #0x14
		LDR r0, [r0, #4]
		LSL r1, r1, #6
		ADD r0, r0, r1
		LDR r0, [r0, #0x38]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x10c60
		MOV r2, #0
		MOV r1, #9
		BL       |List_CallMethod1|
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0x10c60
	INCBIN  baserom.gba_0x10dd8_0x10dda.extracted
|sub_08010DDA|
|unk_08010DDA|
	INCBIN	baserom.gba_0x10dda_0x10dde.extracted
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r0, #0xff
	ADD      r5, r2, #0
	LDR      r2, [pc, #0x14c]
	ADD      r0, #0xc1
	ADD      r7, r1, #0
	MOV      r1, #0x9f
	SUB      sp, #0x14
	STR      r0, [sp, #0x10]
	LSL      r1, r1, #3
	SUB      r2, #0x14
	CMP      r7, #0xa
	LDR      r0, [pc, #0x140]
	BEQ      |loc_08010ECA|
	BGT      |sub_08010E1A|
	ADD      r6, r5, #0
	ADD      r6, #0x14
	ADD      r0, r5, #4
	CMP      r7, #0
	BEQ      |loc_08010EEC|
	CMP      r7, #1
	BEQ      |loc_08010EEE|
	CMP      r7, #2
	BEQ      |loc_08010EF0|
	CMP      r7, #9
	BNE      |loc_08010EF2|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
