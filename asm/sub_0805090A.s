	CODE16
|sub_0805090A|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	STR      r2, [sp, #0x270]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
|loc_0805091C|
	MOV      r1, #0
	ADD      r4, r0, #0
	ADD      r0, #8
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x10]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08050934|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050934|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	STR      r1, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805094A|
	BL       |GBARam_Free|
|loc_0805094A|
	POP      {r3, pc}
|sub_0805094C|
|unk_0805094C|
	INCBIN	baserom.gba_0x5094c_0x5094e.extracted
|sub_0805094E|
	DCW      0x0804
	DCW      0x4a03
