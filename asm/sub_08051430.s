	CODE16
|sub_08051430|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051446|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051446|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_0805145E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805145E|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805146E|
	BL       |GBARam_Free|
|loc_0805146E|
	POP      {r3, pc}
|sub_08051470|
|unk_08051470|
	INCBIN	baserom.gba_0x51470_0x51472.extracted
|sub_08051472|
	DCW      0x0804
