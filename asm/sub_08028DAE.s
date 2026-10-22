	CODE16
|sub_08028DAE|
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4}
	LDR      r1, [pc, #0xd8]
	LDR      r3, [r0, #0x1c]
	LDR      r1, [r1, #4]
	ADD      r2, r0, #0
	ADD      r1, #0x18
	LDR      r4, [r1]
	LDR      r0, [r0, #0x20]
	LDR      r1, [r1, #4]
	SUB      r3, r3, r4
	ADD      r2, #0x24
	SUB      sp, #8
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	LDR      r1, [sp, #4]
	STR      r3, [sp]
	STR      r1, [r2, #4]
	STR      r3, [r2]
	ADD      sp, #8
	POP      {r4}
	MOV      r0, #1
	BX       lr
|loc_08028DEA|
	PUSH     {r4, r5, r6, r7}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x10]
	LDR      r4, [r0, #0x3c]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x24]
	ADD      r3, r4, r6
	LDR      r4, [r5]
	LDR      r6, [r0, #0x28]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r5, [r5, #4]
	ADD      r3, r6, r7
	ADD      r3, r3, r5
	LDR      r7, [pc, #0x88]
	LDRB     r5, [r1, #2]
	LDRB     r6, [r1, #3]
	ADD      r7, #0x28
	LDR      r7, [r7, #8]
	ADD      r5, r4, r5
	ADD      r6, r3, r6
	CMP      r4, r7
	BGE      |loc_08028E94|
	LDR      r7, [pc, #0x74]
	ADD      r7, #0x28
	LDR      r7, [r7]
	CMP      r7, r5
	BGE      |loc_08028E94|
	LDR      r5, [pc, #0x6c]
	ADD      r5, #0x28
	LDR      r7, [r5, #0xc]
	CMP      r3, r7
	BGE      |loc_08028E94|
	LDR      r5, [r5, #4]
	CMP      r5, r6
	BGE      |loc_08028E94|
	LDR      r5, [r2]
	LDR      r1, [r1, #4]
	LDR      r6, [pc, #0x74]
	STR      r1, [r5]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r5, [r1]
	LSR      r4, r4, #7
	AND      r5, r6
	ORR      r4, r5
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_08028E94|
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_08028E98|
	DCW      0x9680
	DCW      0x0804,0xeac4,0x0874,0xcdd4,0x0804,0xefec,0x0874,0x0000
	DCW      0x0601,0xffff,0x0000,0xe454,0x0804,0x8088,0x086b,0xffff
|sub_08028EBA|
|unk_08028EBA|
	INCBIN  baserom.gba_0x28eba_0x28ebc.extracted
		PUSH {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1c
	STR      r0, [sp, #0x18]
	ADD      r6, r1, #0
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r4, #0x34]
	LDR      r2, [r4, #0x30]
	MUL      r1, r0
	MUL      r2, r0
	STR      r2, [sp, #0xc]
	STR      r2, [sp, #0x14]
	ADD      r2, sp, #0x10
	ADD      r0, r1, #0
	STR      r2, [sp]
	STR      r1, [sp, #8]
	ADD      r7, sp, #0x18
	ADD      r2, r7, #0
	MOV      r1, #1
	STR      r0, [sp, #0x10]
	MOV      r3, #2
	ADD      r0, r4, #0
	BL       |loc_08028DEA|
	LDR      r0, [r4, #0x34]
	MOV      r5, #0
	SUB      r0, #1
	CMP      r0, #0
	BLE      |loc_08028F22|
|loc_08028EF8|
	LDR      r0, [r4, #0x2c]
	LDR      r1, [r4, #0x30]
	MUL      r0, r5
	MUL      r1, r5
	STR      r0, [sp]
	ADD      r2, sp, #8
	STR      r2, [sp]
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	MOV      r1, #0
	ADD      r2, r7, #0
	STR      r0, [sp, #8]
	MOV      r3, #0
	ADD      r0, r4, #0
	BL       |loc_08028DEA|
	LDR      r0, [r4, #0x34]
	ADD      r5, #8
	SUB      r0, #1
	CMP      r0, r5
	BGT      |loc_08028EF8|
|loc_08028F22|
	LDR      r0, [sp, #0x18]
	STR      r0, [r6]
	ADD      sp, #0x1c
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	CMP      r1, #0
	SUB      sp, #0xc
	BEQ      |sub_08028F56|
	CMP      r1, #0xb
	BEQ      |loc_08028FC0|
	CMP      r1, #0xc
	BEQ      |loc_08028FE8|
	CMP      r1, #0x26
	BNE      |loc_08028FFA|
	CMP      r4, r2
	BNE      |loc_08028FBC|
	LDR      r0, [pc, #0xc4]
	ADD      r1, r4, #0
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #1
	ADD      sp, #0xc
	POP      {r4, r5, pc}
