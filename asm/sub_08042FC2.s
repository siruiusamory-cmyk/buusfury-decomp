	CODE16
|sub_08042FC2|
	LDR      r1, [pc, #0x390]
	LSL      r0, r4, #1
	ADD      r0, r0, r1
	LDRH     r1, [r0, #0x28]
	SUB      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x28]
	BNE      |loc_08042FD6|
	MOV      r5, #6
|loc_08042FD6|
	LSL      r0, r5, #0x1e
	BPL      |loc_08042FF2|
	LDRB     r0, [r7, #4]
	LDR      r1, [pc, #0x374]
	MOV      r2, #0
	BIC      r0, r6
	STRB     r0, [r7, #4]
	LSL      r0, r4, #1
	ADD      r0, r0, r1
	STRH     r2, [r0, #0x28]
	ADD      r1, r4, #0
	MOV      r0, #8
	BL       |loc_080446a8|
|loc_08042FF2|
	LSL      r0, r5, #0x1d
	BPL      |loc_08042FFE|
	LDR      r1, [pc, #0x35c]
	LDRB     r0, [r1, #0xd]
	ORR      r0, r6
	STRB     r0, [r1, #0xd]
|loc_08042FFE|
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	CMP      r4, #4
	BCC      |loc_08042F2A|
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |loc_0804301C|
	LDR      r5, [pc, #0x344]
	LDR      r0, [sp, #4]
	MOV      r1, #1
	STRH     r0, [r5, #0x14]
	MOV      r0, #0x11
	BL       |loc_0804333c|
|loc_0804301C|
	LDR      r5, [pc, #0x334]
	LDRB     r0, [r5, #0xd]
	CMP      r0, #0
	BEQ      |loc_0804304C|
	LDR      r2, [pc, #0x330]
	LDR      r1, [r2]
	LDRB     r1, [r1, #6]
	CMP      r1, #0
	BEQ      |loc_08043038|
	LDRB     r2, [r5, #3]
	LDRB     r1, [r5]
	AND      r2, r1
	CMP      r2, r1
	BNE      |loc_0804304C|
|loc_08043038|
	BL       |inc_0x042118_0x049114| + 0x1264
	LDRB     r0, [r5, #0xd]
	MOV      r2, #0
	MOV      r1, #1
	STRH     r0, [r5, #0x14]
	STRB     r2, [r5, #0xd]
	MOV      r0, #0x12
	BL       |loc_0804333c|
|loc_0804304C|
	LDRB     r0, [r7, #4]
	CMP      r0, #0
	BNE      |loc_0804306C|
	LDRB     r1, [r5, #4]
	ADD      r0, r5, #0
	CMP      r1, #8
	BNE      |loc_0804306C|
	LDRB     r1, [r0, #7]
	CMP      r1, #0
	BNE      |sub_0804306E|
	MOV      r2, #0
	STRB     r2, [r0, #5]
	STRB     r2, [r0, #4]
	MOV      r0, #0x14
	BL       |loc_0804333c|
|loc_0804306C|
	POP      {r1, r2, r3, r4, r5, r6, r7, pc}
