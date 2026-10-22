	CODE16
|loc_08042E3E|
	LDR      r1, [pc, #0x16c]
	PUSH     {r7, lr}
	LDRB     r0, [r1, #2]
	CMP      r0, #0
	BNE      |loc_08042E52|
	MOV      r1, #0
	MOV      r0, #0x45
	BL       |loc_0804333c|
|loc_08042E50|
	POP      {r7, pc}
|loc_08042E52|
	LDRB     r0, [r1, #2]
	CMP      r0, #1
	BNE      |loc_08042E50|
	MOV      r0, #2
	STRB     r0, [r1, #2]
	POP      {r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x154]
	LDRH     r6, [r7, #8]
	MOV      r5, #0
	STRH     r5, [r7, #8]
	LDR      r4, [pc, #0x140]
	LDRB     r0, [r4, #4]
	CMP      r0, #0xf
	BNE      |loc_08042EB6|
	LDRB     r0, [r4, #0x10]
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	LDRH     r1, [r0, #0x28]
	SUB      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x28]
	BEQ      |loc_08042E90|
	LDRB     r0, [r4, #0x10]
	LDR      r1, [pc, #0x12c]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDRH     r0, [r0]
	CMP      r0, #0x27
	BNE      |loc_08042EB6|
|loc_08042E90|
	BL       |loc_08042E3E|
	MOV      r0, #0x18
	STRB     r0, [r4, #4]
	LDRB     r1, [r4, #0x10]
	MOV      r0, #4
	BL       |loc_080446a8|
	LDRB     r0, [r4, #0x10]
	ADD      r1, r4, #0
	ADD      r1, #0x20
	MOV      r3, #1
	LDRB     r2, [r1, #4]
	LSL      r3, r0
	BIC      r2, r3
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	STRB     r2, [r1, #4]
	STRH     r5, [r0, #0x28]
|loc_08042EB6|
	STRH     r6, [r7, #8]
	LDRB     r0, [r4, #4]
	CMP      r0, #0x18
	BNE      |loc_08042EEA|
	LDRB     r0, [r4, #2]
	CMP      r0, #1
	BNE      |loc_08042EC8|
	BL       |loc_08042E3E|
|loc_08042EC8|
	LDRB     r0, [r4, #2]
	CMP      r0, #0
	BNE      |loc_08042EEA|
	STRB     r5, [r4, #5]
	LDR      r0, [pc, #0xdc]
	STRB     r5, [r4, #4]
	LDR      r0, [r0]
	LDRB     r1, [r0, #2]
	LDRB     r0, [r0, #3]
	ORR      r0, r1
	BL       |inc_0x042118_0x049114| + 0x1264
	MOV      r1, #1
	MOV      r0, #0x25
	STRH     r5, [r4, #0x14]
	BL       |loc_0804333c|
|loc_08042EEA|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0xbc]
	LDRB     r0, [r5, #4]
	CMP      r0, #5
	BCC      |loc_08042FC0|
	CMP      r0, #8
	BHI      |loc_08042FC0|
	LDR      r6, [pc, #0xb4]
	LDRB     r2, [r5, #0xc]
	LDR      r1, [r6]
	LDRB     r0, [r1, #2]
	LDRB     r1, [r1, #7]
	EOR      r2, r0
	AND      r2, r0
	BIC      r2, r1
	STR      r2, [sp, #8]
	STRB     r0, [r5, #0xc]
	LDR      r2, [sp, #8]
	CMP      r2, #0
	BEQ      |loc_08042F20|
	LDR      r0, [sp, #8]
	MOV      r1, #1
	STRH     r0, [r5, #0x14]
	MOV      r0, #0x10
	BL       |loc_0804333c|
|loc_08042F20|
	MOV      r0, #0
	LDR      r7, [pc, #0x88]
	MOV      r4, #0
	ADD      r7, #0x20
	STR      r0, [sp, #4]
|loc_08042F2A|
	MOV      r0, #1
	LSL      r0, r4
	LSL      r6, r0, #0x18
	LDR      r0, [sp, #8]
	LSR      r6, r6, #0x18
	MOV      r5, #0
	AND      r0, r6
	BEQ      |sub_08042F4C|
	LDR      r5, [pc, #0x70]
	LSL      r1, r4, #1
	LDRH     r0, [r5, #0x26]
	ADD      r1, r1, r5
	STRH     r0, [r1, #0x28]
	LDRB     r0, [r7, #4]
	ORR      r0, r6
	STRB     r0, [r7, #4]
	B        |loc_08042FFE|
