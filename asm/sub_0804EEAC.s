	CODE16
|sub_0804EEAC|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EEC8|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0xc]
	STR      r2, [r0]
	STR      r1, [r0, #0x10]
|loc_0804EEC8|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LDR      r6, [sp, #0x3b0]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	ADD      r1, r0, #0
	MOV      r0, #0
	BL       |Object_Create1|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EEF6|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	LDR      r1, [pc, #4]
	STR      r1, [r0]
|loc_0804EEF6|
	POP      {r4, pc}
|sub_0804EEF8|
|unk_0804EEF8|
	INCBIN	baserom.gba_0x4eef8_0x4eefa.extracted
|sub_0804EEFA|
	DCW      0x0804
