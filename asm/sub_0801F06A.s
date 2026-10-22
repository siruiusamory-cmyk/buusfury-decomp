	CODE16
|sub_0801F06A|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	STMIA    r3!, {r4, r6}
	LSL      r0, r0, #0
|loc_0801F07C|
	LSL      r0, r4, #0
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	ADD      r4, r0, #0
	BL       |loc_08024120|
	MOV      r0, #0xff
	ADD      r3, sp, #0
	STRB     r0, [r3, #9]
	ADD      r4, #0xff
	ADD      r4, #1
	MOV      r0, #0xff
	ADD      r0, #0x35
	LDR      r7, [r4, #0x18]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0801F0EC|
	LDR      r0, [pc, #0x1ac]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #4
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #5
	ADD      r0, r4, #0
	STR      r6, [r5, #0x20]
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r6, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x180]
	LDR      r1, [pc, #0x184]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x17c]
	STR      r6, [r0]
	LDR      r0, [pc, #0x180]
	STR      r6, [r1]
	STR      r0, [r4]
	STR      r6, [r5, #0x2c]
	STR      r6, [r1]
	STR      r7, [r5, #0x30]
|loc_0801F0EC|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x164]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0801F118|
	MOV      r0, #2
	POP      {r4, pc}
|loc_0801F118|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r4, pc}
	ADD      r3, r0, #0
	ADD      r3, #0xff
	PUSH     {r4, r5, r6, r7}
	ADD      r3, #1
	LDR      r0, [r3, #0x30]
	MOV      r5, #0x5d
	LSL      r5, r5, #5
	ADD      r0, r0, r5
	LDR      r0, [r0]
	STRB     r0, [r1]
	LDR      r0, [pc, #0x128]
	LDR      r2, [r0]
	MOV      r0, #2
	STRB     r2, [r1, #1]
	LDRB     r4, [r1]
	MOV      r2, #0
	CMP      r4, #0
	BLE      |loc_0801F180|
|loc_0801F144|
	LDR      r4, [r3, #0x30]
	ADD      r6, r4, r5
	LSL      r4, r2, #3
	ADD      r6, r4, r6
	LDR      r7, [r6, #4]
	ADD      r6, r0, #1
	STRB     r7, [r1, r0]
	LDR      r0, [r3, #0x30]
	ADD      r2, #1
	ADD      r0, r0, r5
	ADD      r0, r4, r0
	LDR      r0, [r0, #4]
	LSR      r7, r0, #8
	STRB     r7, [r1, r6]
	ADD      r0, r6, #1
	LDR      r6, [r3, #0x30]
	ADD      r6, r6, r5
	ADD      r6, r4, r6
	LDRB     r7, [r6, #8]
	ADD      r6, r0, #1
	STRB     r7, [r1, r0]
	LDR      r0, [r3, #0x30]
	ADD      r0, r0, r5
	ADD      r0, r4, r0
	LDRB     r4, [r0, #9]
	ADD      r0, r6, #1
	STRB     r4, [r1, r6]
	LDRB     r4, [r1]
	CMP      r4, r2
	BGT      |loc_0801F144|
|loc_0801F180|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801F184|
|unk_0801F184|
		PUSH {r4, r5, r6, r7}
		SUB r2, #3
		CMP r2, #5
		SUB sp, #8
		BHS      |loc_0801F21A|
		ADR      r3, |loc_0801F198|
		LDRB r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
		LSL r0, r0, #0
|loc_0801F198|
		LSL r1, r0, #0xd
		ADD r4, r8
		LSL r4, r0, #1
		LDRB r4, [r1]
		LDRB r3, [r1, #1]
		MOV r2, #2
		CMP r3, #0
		BEQ      |sub_0801F1AC|
		MOV r3, #1
		DCW     0xE000
