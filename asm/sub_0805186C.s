	CODE16
|sub_0805186C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08051882|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051882|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_0805189A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805189A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080518B2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080518B2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080518C2|
	BL       |GBARam_Free|
|loc_080518C2|
	POP      {r3, pc}
|sub_080518C4|
|unk_080518C4|
	INCBIN	baserom.gba_0x518c4_0x518c6.extracted
|sub_080518C6|
	DCW      0x0804
