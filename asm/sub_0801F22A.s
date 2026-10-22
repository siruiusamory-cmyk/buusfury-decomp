	CODE16
|sub_0801F22A|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	LDR      r0, [r1, #0x30]
	LDR      r3, [pc, #0x38]
	ADD      r0, r0, r3
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_0801F250|
|loc_0801F23C|
	LDR      r0, [r1, #0x30]
	ADD      r0, r0, r3
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	LDR      r0, [r1, #0x30]
	ADD      r0, r0, r3
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |loc_0801F23C|
|loc_0801F250|
	BX       lr
|sub_0801F252|
	DCW      0x0000
	DCW      0x92ec,0x0804,0xffff
|sub_0801F25A|
	LSL      r0, r0, #0
	CMP      r7, #0x50
	LSL      r0, r0, #0xc
	CMP      r7, #0x54
	LSL      r0, r0, #0xc
	STMIA    r5!, {r3, r5, r6, r7}
	LSR      r4, r0, #0x20
	LSR      r0, r6, #0x1f
	LSL      r0, r0, #0xc
	LSR      r4, r1, #0xf
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	BL       |loc_08024120|
	ADD      r4, #0xff
	ADD      r4, #0x11
	MOV      r0, #0xff
	ADD      r0, #0x31
	LDRB     r7, [r4, #8]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0801F2D6|
	LDR      r0, [pc, #0x100]
	MOV      r1, #0xff
	STR      r0, [r4]
	MOV      r0, #6
	ADD      r1, #0x15
	STRB     r0, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	MOV      r6, #0
	STR      r6, [r5, #0x1c]
	SUB      r1, r0, #7
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
	LDR      r0, [pc, #0xd4]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0xd4]
	STR      r6, [r0]
	LDR      r0, [pc, #0xd4]
	STR      r6, [r0]
	LDR      r0, [pc, #0xd4]
	STR      r0, [r4]
	ADD      r0, r5, #0
	ADD      r0, #0x20
	STRB     r6, [r0, #0xe]
	STRB     r6, [r0, #0xf]
	STRB     r6, [r0, #0xd]
	STRB     r7, [r0, #0xc]
|loc_0801F2D6|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	BL       |sub_0802426E|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0xb4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LSL      r1, r0, #0x18
	LSR      r1, r1, #0x18
	BEQ      |loc_0801F308|
	MOV      r0, #2
	CMP      r1, #1
	BEQ      |loc_0801F306|
	MOV      r0, #3
|loc_0801F306|
	POP      {r4, pc}
|loc_0801F308|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x669c
	POP      {r4, pc}
	ADD      r0, #0xff
	ADD      r0, #0x21
	LDRB     r2, [r0, #0xc]
	STRB     r2, [r1]
	LDRB     r0, [r0, #0xd]
	STRB     r0, [r1, #1]
	MOV      r0, #2
	BX       lr
|sub_0801F320|
|unk_0801F320|
		SUB r2, #3
		CMP r2, #5
		BHS      |loc_0801F364|
		ADR      r3, |loc_0801F330|
		LDRB r3, [r3, r2]
		LSL r3, r3, #1
		ADD pc, r3
		LSL r0, r0, #0
|loc_0801F330|
		LSL r3, r0, #0xc
		LSR r2, r3, #0xc
		LSL r3, r2, #0
		ADD r1, r0, #0
		ADD r1, #0xff
		MOV r2, #2
		ADD r1, #0x21
		STRB r2, [r1, #0xd]
		LDRB r2, [r1, #0xc]
		STRB r2, [r1, #0xe]
		B        |loc_0801F364|
	INCBIN  baserom.gba_0x1f346_0x1f364.extracted
|loc_0801F364|
		ADD r0, #0xff
		ADD r0, #0x21
		LDRB r2, [r0, #0xd]
		CMP r2, #0
		DCW     0xD00C
		LDRB r1, [r0, #0xc]
		CMP r1, #0
		DCW     0xD009
		LDRB r3, [r0, #0xe]
		CMP r1, r3
		DCW     0xD106
		CMP r1, #1
		BNE      |sub_0801F384|
		CMP r2, #1
		BNE      |sub_0801F384|
		DCW     0xE000
