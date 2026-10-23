	CODE16
|sub_08052888|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080528A2|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080528A2|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080528B0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080528B0|
	POP      {r3, r4, r5, pc}
|loc_080528B2|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xcf28,0x0874,0xe454
|loc_080528C2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080528DE|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080528DE|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080528EC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080528EC|
	POP      {r3, r4, r5, pc}
|loc_080528EE|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x7b54,0x0875,0xe454
|loc_080528FE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805291A|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805291A|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052928|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052928|
	POP      {r3, r4, r5, pc}
|loc_0805292A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xd03c,0x0874,0xe454
|loc_0805293A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052956|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052956|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052964|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052964|
	POP      {r3, r4, r5, pc}
|loc_08052966|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xd248,0x0874,0xe454
|loc_08052976|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052992|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052992|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080529A0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080529A0|
	POP      {r3, r4, r5, pc}
|loc_080529A2|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xcf28,0x0874,0xe454
|loc_080529B2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080529CA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080529CA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080529E2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080529E2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080529FA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080529FA|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052A0A|
	BL       |GBARam_Free|
|loc_08052A0A|
	POP      {r3, pc}
|sub_08052A0C|
|unk_08052A0C|
	INCBIN	baserom.gba_0x52a0c_0x52a0e.extracted
|sub_08052A0E|
	DCW      0x0804
