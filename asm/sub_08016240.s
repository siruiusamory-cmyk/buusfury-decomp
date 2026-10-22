	CODE16
|sub_08016240|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x78]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0xc]
	BL       |GBARam_Free|
	LDR      r0, [pc, #0x74]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0801625E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0801625E|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #8]
	ADD      r6, r1, #0
	LSL      r0, r0, #0x1c
	SUB      sp, #0x10
	BMI      |loc_080162A4|
	LDR      r0, [r4, #4]
	MOV      r5, sp
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r2, r2, r1
	MOV      r1, sp
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_080162A4|
	LDR      r0, [sp]
	ADD      r2, r5, #0
	SUB      r0, #0x10
	STR      r0, [sp]
	LDR      r0, [sp, #4]
	SUB      r0, #8
	STR      r0, [sp, #4]
	LDR      r0, [sp]
	ADD      r0, #0x10
	STR      r0, [sp, #8]
	LDR      r0, [sp, #4]
	ADD      r0, #0x10
	STR      r0, [sp, #0xc]
	LDR      r1, [r4, #0xc]
	ADD      r0, r6, #0
	BL       |inc_0x03d784_0x041118| + 0x219e
|loc_080162A4|
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
	LDR      r1, [r0, #8]
	ADD      r1, #1
	STR      r1, [r0, #8]
	LSL      r1, r1, #0x1d
	BNE      |loc_080162BC|
	LDR      r1, [r0, #4]
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r0, [r1, #0x10]
|loc_080162BC|
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [sp, #0x260]
	LSR      r4, r0, #0x20
	LDRB     r4, [r1, #0x1a]
	LSR      r3, r5, #1
	STR      r2, [sp, #0x270]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	LDR      r2, [r1, #4]
	LDR      r1, [r0, #8]
	ADD      r3, r0, #0
	MOV      r0, #0
	BL       |loc_08016304|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r2, [r1, #4]
	LDR      r1, [r0, #8]
	MOV      r3, #0
	MOV      r0, #0
	BL       |loc_08016304|
	ADD      r1, r0, #0
	LDR      r0, [pc, #8]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	POP      {r3, pc}
|sub_08016300|
|unk_08016300|
	INCBIN	baserom.gba_0x16300_0x16302.extracted
