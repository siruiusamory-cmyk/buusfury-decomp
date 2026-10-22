	CODE16
|sub_0803B16A|
	MOV      r0, #1
	CMP      r2, #0
	BLE      |loc_0803B172|
|loc_0803B170|
	MOV      r0, #0
|loc_0803B172|
	ADD      r3, sp, #0x20
	STRB     r0, [r3]
	LDR      r0, [pc, #0x60]
	ADD      r2, sp, #0x14
	STR      r0, [sp, #0x28]
	LDR      r0, [r5]
	MOV      r1, #0x28
	BL       |inc_0x0158_0x143f2| + 0x11b18
	LDRB     r0, [r6]
	CMP      r0, #2
	BNE      |loc_0803B1A8|
	LDR      r0, [r4, #0x10]
	MOV      r1, #0x80
	ASR      r0, r0, #8
	SUB      r0, r1, r0
	MOV      r3, #0x32
	MUL      r0, r3
	ASR      r1, r0, #6
	CMP      r1, #0
	BGT      |loc_0803B1A0|
	MOV      r1, #0
	STRB     r7, [r6]
|loc_0803B1A0|
	MOV      r2, #0x64
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x95d0
|loc_0803B1A8|
	LDRB     r0, [r6]
	CMP      r0, #3
	BEQ      |loc_0803B1B2|
	CMP      r0, #1
	BNE      |loc_0803B1BA|
|loc_0803B1B2|
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0803B1BA|
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	ADD      r0, sp, #0x210
	LSR      r4, r0, #0x20
|unk_0803B1C4|
	INCBIN	baserom.gba_0x3b1c4_0x3b1c6.extracted
	LSR      r7, r6, #1
	ADD      r2, #0xe4
	LSL      r0, r0, #0xc
	BLS      |loc_0803B170|
	LSR      r7, r5, #1
	LDMIA    r4!, {r0, r2, r3, r6, r7}
|unk_0803B1D2|
	INCBIN	baserom.gba_0x3b1d2_0x3b1d4.extracted
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	LDR      r0, [r0, #0xc]
	ASR      r1, r1, #8
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	BL       |loc_0803A7FC|
	MOV      r0, #0
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	MOV      r6, #0
	ADD      r4, r0, #0
	CMP      r1, #0
	BNE      |loc_0803B23C|
	LDR      r0, [r2, #0x30]
	CMP      r0, r4
	BNE      |loc_0803B204|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
|loc_0803B204|
	LDR      r0, [r2, #0x1c]
	LDRB     r0, [r0]
	CMP      r0, #1
	BNE      |sub_0803B238|
	ADD      r1, r2, #4
	ADD      r0, r4, #0
	BL       |sub_0803AF58|
	CMP      r0, #0
	BEQ      |sub_0803B238|
	LDR      r0, [pc, #0xbc]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |sub_0803B238|
	LDR      r5, [r4, #0x10]
	CMP      r5, #0
	BLE      |loc_0803B234|
	LDR      r0, [pc, #0xb4]
	BL       |inc_0x049120_0x055620| + 0xb944
	SUB      r0, r5, r0
	STR      r0, [r4, #0x10]
	BPL      |loc_0803B234|
	STR      r6, [r4, #0x10]
|loc_0803B234|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
