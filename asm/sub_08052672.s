	CODE16
|sub_08052672|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r5, #0
	BEQ      |loc_08052694|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052694|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	LDMIA    r7!, {r3, r4, r5, r7}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_080526B2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080526B2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080526C2|
	BL       |GBARam_Free|
|loc_080526C2|
	POP      {r3, pc}
|sub_080526C4|
|unk_080526C4|
	INCBIN	baserom.gba_0x526c4_0x526c6.extracted
