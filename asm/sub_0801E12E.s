	CODE16
|sub_0801E12E|
|unk_0801E12E|
		CMP r1, #0
		DCW     0xD104
		LDR r1, [r0, #0x44]
		CMP r1, #0
		DCW     0xD101
		MOV r0, #0
		DCW     0xE7F7
	INCBIN  baserom.gba_0x1e13c_0x1e13e.extracted
|sub_0801E13E|
|unk_0801E13E|
	INCBIN	baserom.gba_0x1e13e_0x1e142.extracted
	LSL      r0, r0, #0
	PUSH     {r7}
	LSR      r4, r0, #0x20
	LSL      r0, r5, #0xb
	LSR      r2, r6, #1
|loc_0801E14C|
	PUSH     {lr}
	LDR      r1, [r0, #0x30]
	MOV      r0, #0
	SUB      sp, #0x6c
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	MOV      r2, #0
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	ADD      sp, #0x6c
	POP      {pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	LDRB     r1, [r0]
	MOV      r6, #0
	ADD      r4, r2, #0
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	CMP      r1, #0
	SUB      sp, #0x70
	BEQ      |sub_0801E18A|
	LDR      r1, [r0, #0x30]
	STR      r6, [sp, #4]
	STR      r6, [sp, #0x48]
	ADD      r0, sp, #4
	MOV      r2, #0
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	ADD      sp, #0x70
	POP      {r4, r5, r6, pc}
