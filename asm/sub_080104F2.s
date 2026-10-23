	CODE16
|sub_080104F2|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_0801050E|
	MOV      r0, #9
	LSL      r0, r0, #6
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0801050E|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0801050E|
	MOV      r3, #1
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |loc_080109AA|
	LDR      r0, [pc, #0x64]
	STR      r0, [r4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08010534|
	LDR      r1, [pc, #0x58]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #4]
|loc_08010534|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800ED18|
	MOV      r1, #0xf
	ADD      r0, r4, #0
	BL       |Record_SelectIndexed|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08010562|
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #4]
|loc_08010562|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |loc_0800ED18|
	POP      {r4, pc}
	PUSH     {r3, lr}
	BL       |loc_0800EF08|
	POP      {r3, pc}
|sub_08010574|
|unk_08010574|
; cited by 0x080103A8 (a pc-relative load targets 0x08010578)
		BX       lr
	INCBIN  baserom.gba_0x10576_0x10582.extracted
|sub_08010582|
	DCW      0x0804
	DCW      0xd038
	DCW      0x0804
	DCW      0x4896
