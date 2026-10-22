	CODE16
|sub_08015A96|
	LSL      r0, r0, #0xc
	CMP      r2, #0x58
	LSL      r0, r0, #0xc
	STRH     r0, [r6, #2]
	LSR      r3, r5, #1
	LDRB     r0, [r0, #8]
	LDR      r1, [r1, #4]
	STRB     r0, [r1, #0x10]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0, #8]
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x7824
	POP      {r3, pc}
	LDR      r1, [r0, #0xc]
	SUB      r1, #1
	STR      r1, [r0, #0xc]
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r5, #8]
	MOV      r0, #0xff
	ADD      r0, #0xa1
	LSL      r1, r1, #8
	STR      r1, [r0, r4]
	LDR      r1, [r5, #0xc]
	ADD      r0, #4
	LSL      r1, r1, #8
	STR      r1, [r0, r4]
|loc_08015AE0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08015B04|
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08015B1C|
|loc_08015B04|
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r1, [r0, #0x20]
	MOV      r1, #1
	MOV      r2, #0x24
	STRB     r1, [r2, r0]
	LDR      r1, [pc, #0x50]
	STR      r1, [r0]
	STR      r4, [r0, #0x28]
	LDMIA    r5!, {r2, r3}
	STR      r2, [r0, #0x2c]
	STR      r3, [r0, #0x30]
|loc_08015B1C|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r2, [r0, #0x28]
	SUB      sp, #0x10
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	LDR      r2, [r2]
	ASR      r3, r3, #8
	ASR      r2, r2, #8
	STR      r2, [sp, #4]
	ADD      r2, r3, #0
	STR      r3, [sp]
	LDR      r3, [sp, #4]
	STR      r2, [sp, #8]
	STR      r3, [sp, #0xc]
	LDR      r3, [r0, #0x2c]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0xc]
	LDR      r4, [r0, #0x30]
	STR      r2, [sp]
	ADD      r3, r3, r4
	STR      r3, [sp, #4]
	ADD      r3, r2, #0
	MOV      r2, #0x64
	LDR      r4, [sp, #4]
	STR      r2, [r0, #8]
	STR      r3, [r0, #0x14]
	STR      r4, [r0, #0x18]
	MOV      r2, #0
	STR      r2, [r0, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x421e
	ADD      sp, #0x10
	POP      {r4, pc}
	LSL      r0, r0, #0
	BMI      |loc_08015AE0|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08015B82|
	MOV      r0, #4
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08015B82|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08015B82|
	LDR      r0, [pc, #0x2c]
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	STR      r0, [r4]
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0x7700
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ca2
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	LDR      r0, [pc, #0x14]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4c92
	MOV      r1, #1
	SUB      r0, r1, r0
	POP      {r3, pc}
	LSL      r0, r0, #0
	BCS      |loc_08015CAC|
	LSR      r4, r0, #0x20
	STRH     r4, [r6, #2]
	LSR      r3, r5, #1
