	CODE16
|sub_08036964|
|unk_08036964|
; cited by 0x0803678C (a pc-relative load targets 0x08036968)
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x36968_0x3696e.extracted
|sub_0803696E|
|unk_0803696E|
	INCBIN	baserom.gba_0x3696e_0x36972.extracted
	MOV      r0, #0
	MOV      r0, #0
	ADD      r0, #0
	MOV      r0, #0
	ASR      r0, r0, #0x20
	STR      r0, [r0]
	STRH     r0, [r0]
	MOV      r0, #0x88
	LSR      r0, r4
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r4, [pc, #0x80]
	ADD      r6, r1, #0
	MOV      r2, #1
	MOV      r1, #0x22
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0xdc36
	ADD      r5, r0, #0
	MOV      r2, #0
	MOV      r1, #0x22
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080369CE|
	MOV      r1, #0x32
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	MOV      r1, #0
	STR      r1, [r0, #0x14]
	LDR      r1, [pc, #0x48]
	STR      r1, [r0]
|loc_080369CE|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r4, [pc, #0x38]
	ADD      r6, r1, #0
	MOV      r2, #1
	MOV      r1, #0x22
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x3848
	ADD      r5, r0, #0
	MOV      r2, #0
	MOV      r1, #0x22
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	ADD      r0, r5, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08036A0E|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08036A0E|
	POP      {r4, pc}
|sub_08036A10|
|unk_08036A10|
	INCBIN	baserom.gba_0x36a10_0x36a12.extracted
