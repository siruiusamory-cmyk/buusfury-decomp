	CODE16
|sub_08015A26|
	LSR      r3, r5, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x18]
	SUB      r1, #1
	STR      r1, [r0, #0x18]
	LDR      r2, [r0, #0x1c]
	CMP      r1, r2
	BLE      |loc_08015A42|
	LDR      r2, [r0, #0x14]
	SUB      r1, r2, r1
|loc_08015A42|
	LDR      r3, [r0, #0x20]
	MUL      r3, r1
	ADD      r0, #8
	LDMIA    r0!, {r0, r1, r2}
	BL       |inc_0x0158_0x143f2| + 0x6f1c
	POP      {r3, pc}
	ADD      r1, r0, #0
	LDR      r1, [r1, #0x18]
	MOV      r0, #1
	CMP      r1, #0
	BEQ      |loc_08015A5C|
	MOV      r0, #0
|loc_08015A5C|
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r1, #4]
	LDR      r1, [pc, #0x2c]
	MOV      r0, #1
	LDR      r1, [r1]
	CMP      r4, r1
	BNE      |loc_08015A72|
	LDR      r1, [pc, #0x28]
	STR      r0, [r1]
|loc_08015A72|
	LDR      r5, [pc, #0x28]
	ADD      r2, r4, #0
	MOV      r1, #0x12
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r4, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	POP      {r3, r4, r5, pc}
|sub_08015A94|
|unk_08015A94|
	INCBIN	baserom.gba_0x15a94_0x15a96.extracted
