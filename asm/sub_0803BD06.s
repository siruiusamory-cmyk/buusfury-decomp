	CODE16
|sub_0803BD06|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	SUB      sp, #0x10
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0x34
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
	LDR      r0, [pc, #0x60]
	MOV      r1, #5
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	CMP      r0, #0
	BEQ      |loc_0803BD60|
	MOV      r1, #0
	LDR      r2, [pc, #0x54]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0803BD44|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0803BD44|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0x40]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0803BD60|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803BD60|
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r3, lr}
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803BD80|
	MOV      r1, #0xb3
	STR      r1, [r0, #4]
	MOV      r1, #0x32
	STR      r1, [r0, #8]
	MOV      r1, #0
	STR      r1, [r0, #0x14]
	LDR      r1, [pc, #0x10]
	STR      r1, [r0]
|loc_0803BD80|
	POP      {r3, pc}
	LSL      r0, r0, #0
|unk_0803BD84|
	INCBIN	baserom.gba_0x3bd84_0x3bd86.extracted
	LSR      r7, r6, #1
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0x300
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, lr}
	SUB      sp, #0x1c
	ADD      r4, r0, #0
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x24
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	LDRB     r0, [r1, #0x10]
	LDR      r2, [pc, #0x16c]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, r0, r2
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	LDR      r2, [r2]
	ASR      r3, r3, #8
	ASR      r2, r2, #8
	STR      r2, [sp, #8]
	ADD      r2, r3, #0
	STR      r3, [sp, #4]
	LDR      r3, [sp, #8]
	STR      r2, [sp, #0xc]
	STR      r3, [sp, #0x10]
	LDR      r3, [r0]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0x10]
	LDR      r5, [r0, #4]
	STR      r2, [sp, #4]
	ADD      r3, r3, r5
	STR      r2, [sp, #0x14]
	LDR      r2, [pc, #0x13c]
	STR      r3, [sp, #8]
	STR      r3, [sp, #0x18]
	ADD      r3, r1, #0
	STR      r2, [sp]
	LDR      r2, [r0, #8]
	MOV      r0, #0
	ADD      r1, sp, #0x14
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4e8e
	ADD      r1, r0, #0
	STR      r0, [r4, #4]
	LDR      r0, [pc, #0x120]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0x3c
	STR      r0, [r4, #8]
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
|sub_0803BE02|
|unk_0803BE02|
		BX       lr
