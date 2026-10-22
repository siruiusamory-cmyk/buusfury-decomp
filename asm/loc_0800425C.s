	CODE16
|loc_0800425C|
	PUSH     {r4, r5, r6, lr}
	LDRB     r1, [r0, #1]
	ADD      r4, r0, #0
	MOV      r2, #0x13
	LSL      r2, r2, #6
	LSL      r0, r1, #0x1d
	LSR      r0, r0, #0x1f
	ADD      r5, r4, r2
	CMP      r0, #0
	SUB      sp, #0x10
	BEQ      |loc_08004288|
	LDR      r0, [r5, #0x14]
	SUB      r0, #1
	STR      r0, [r5, #0x14]
	BNE      |loc_08004288|
	MOV      r0, #4
	BIC      r1, r0
	STRB     r1, [r4, #1]
	MOV      r1, #0
	LDR      r0, [pc, #0x294]
	BL       |sub_08012588|
|loc_08004288|
	LDRB     r1, [r4, #1]
	LSL      r0, r1, #0x1b
	LSR      r0, r0, #0x1f
	BEQ      |loc_080042AA|
	LDR      r0, [r5, #0x18]
	LDR      r2, [pc, #0x288]
	ADD      r0, #1
	STR      r0, [r5, #0x18]
	CMP      r0, r2
	BCC      |loc_080042AA|
	MOV      r0, #0x10
	BIC      r1, r0
	STRB     r1, [r4, #1]
	MOV      r1, #0
	LDR      r0, [pc, #0x278]
	BL       |sub_08012588|
|loc_080042AA|
	LDR      r0, [r5, #0x1c]
	LDR      r6, [pc, #0x274]
	CMP      r0, #0
	BEQ      |loc_080042C2|
	SUB      r0, #1
	STR      r0, [r5, #0x1c]
	BNE      |loc_080042C2|
	LDR      r0, [r6]
	CMP      r0, #0
	BEQ      |loc_080042C2|
	BL       |loc_0801064C|
|loc_080042C2|
	LDRB     r0, [r4, #1]
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1f
	BEQ      |loc_080042F8|
	LDR      r1, [r6]
	CMP      r1, #0
	BEQ      |loc_080042F8|
	LDR      r0, [pc, #0x254]
	LDR      r5, [r0, #0xc]
	MOV      r0, sp
	BL       |sub_0800FDFA|
	ADD      r5, #0x80
	LDR      r1, [r5, #0x2c]
	MOV      r0, sp
	BL       |loc_08009324|
	CMP      r0, #0
	BNE      |loc_080042F8|
	LDRB     r0, [r4, #1]
	MOV      r1, #0x20
	BIC      r0, r1
	STRB     r0, [r4, #1]
	LDR      r0, [pc, #0x238]
	MOV      r1, #0
	BL       |sub_08012588|
|loc_080042F8|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
