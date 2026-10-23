	CODE16
|sub_0804F3B4|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	BEQ      |loc_0804F3EC|
	LDR      r0, [pc, #0x2c]
	MOV      r5, #0
	STR      r0, [r4]
	LDR      r0, [r4, #4]
	CMP      r0, #0
	BLE      |loc_0804F3E6|
|loc_0804F3CE|
	LSL      r0, r5, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #4]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_0804F3CE|
|loc_0804F3E6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0804F3EC|
	POP      {r3, r4, r5, pc}
|sub_0804F3EE|
|unk_0804F3EE|
	INCBIN	baserom.gba_0x4f3ee_0x4f3f2.extracted
|sub_0804F3F2|
	DCW      0x0804
