	CODE16
|sub_080527D6|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_080527EE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080527EE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052806|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052806|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x20]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BEQ      |loc_08052824|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08052824|
	CMP      r5, #0
	BEQ      |loc_0805282E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805282E|
	POP      {r3, r4, r5, pc}
|sub_08052830|
|unk_08052830|
	INCBIN	baserom.gba_0x52830_0x52832.extracted
