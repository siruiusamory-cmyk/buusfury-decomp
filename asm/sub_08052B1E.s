	CODE16
|sub_08052B1E|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x30]
	ADD      r5, r1, #0
	LDR      r1, [pc, #0x30]
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r1]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xe5a0
	CMP      r5, #0
	BEQ      |loc_08052B56|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052B56|
	POP      {r3, r4, r5, pc}
|sub_08052B58|
|unk_08052B58|
	INCBIN	baserom.gba_0x52b58_0x52b5a.extracted
