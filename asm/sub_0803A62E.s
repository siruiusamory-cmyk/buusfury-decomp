	CODE16
|sub_0803A62E|
	LSL      r0, r0, #0xc
	ADD      r2, #0xd0
	LSL      r0, r0, #0xc
	ADR      r1, |loc_0803A7D8|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x58]
	SUB      sp, #0x24
	LDR      r6, [pc, #0x54]
	MOV      r4, #0
	SUB      r7, #0x20
	ADD      r5, sp, #4
|loc_0803A646|
	MOV      r2, #0x20
	ADD      r1, r7, #0
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LSL      r0, r4, #3
	LDR      r1, [r6, r0]
	ADD      r3, sp, #0
	STRH     r1, [r3, #0x10]
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x38]
	STRH     r0, [r3, #0x12]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x18]
	SUB      r0, #0x24
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r4, #1
	CMP      r4, #5
	BLT      |loc_0803A646|
	MOV      r0, #1
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|sub_0803A68E|
|unk_0803A68E|
	INCBIN	baserom.gba_0x3a68e_0x3a692.extracted
