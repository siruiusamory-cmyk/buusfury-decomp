	CODE16
|sub_08029584|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x3c]
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r5, r2, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	SUB      sp, #4
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_080295B6|
	ADD      r3, r5, #0
	ADD      r2, r6, #0
	MOV      r0, #0
	STR      r7, [sp]
	LDR      r1, [sp, #4]
	BL       |loc_08029384|
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_080295B6|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
|unk_080295BC|
	INCBIN	baserom.gba_0x295bc_0x295be.extracted
	LSR      r4, r0, #0x20
	LSL      r4, r5, #7
	LSR      r5, r6, #1
	DCW      0xf08c,0x0874
	STR      r4, [sp, #0x100]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSL      r4, r0, #8
	LSR      r5, r6, #1
	STRH     r0, [r3, #6]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0xa0]
	ADD      r6, r1, #0
	LDR      r1, [r0]
	MOV      r4, #0
	CMP      r1, #0
	SUB      sp, #0x40
	BEQ      |loc_0802965A|
	ADD      r0, sp, #8
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	ADD      r0, sp, #0x20
	ADD      r1, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #0x20]
	LDR      r1, [sp, #0x28]
	LDR      r2, [sp, #0x2c]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x24]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x34]
	ASR      r1, r1, #1
	LDR      r0, [sp, #0x18]
	STR      r1, [sp]
	STR      r1, [sp, #0x30]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x1c]
	LDR      r2, [sp, #0x34]
	STR      r1, [sp]
	SUB      r0, r0, r2
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x3c]
	ADD      r0, r1, #0
	MUL      r0, r1
	STR      r1, [sp, #0x38]
	LDR      r1, [sp, #0x3c]
	ADD      r2, r1, #0
	MUL      r1, r2
	ADD      r0, r0, r1
	LDR      r1, [r5, #0xc]
	CMP      r0, r1
	BLE      |loc_0802965A|
	MOV      r4, #1
|loc_0802965A|
	ADD      r0, r4, #0
	ADD      sp, #0x40
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029680|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08029680|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	ADD      r6, pc, #0x3A0
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080296A0|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080296A0|
	POP      {r4, pc}
	LDR      r0, [r0, #0xc]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0x24]
	MOV      r0, #0
	BX       lr
|sub_080296AE|
|unk_080296AE|
	INCBIN	baserom.gba_0x296ae_0x296b2.extracted
