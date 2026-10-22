	CODE16
|sub_08052D12|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08052D2A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052D2A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052D42|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052D42|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052D5A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052D5A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052D72|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052D72|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052D8E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052D8E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052D9C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052D9C|
	POP      {r3, r4, r5, pc}
|loc_08052D9E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xbf94,0x0872,0xe454
|loc_08052DAE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x10a28
	CMP      r5, #0
	BEQ      |loc_08052DC6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052DC6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052DDE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052DDE|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052DEE|
	BL       |GBARam_Free|
|loc_08052DEE|
	POP      {r3, pc}
|sub_08052DF0|
|unk_08052DF0|
	INCBIN	baserom.gba_0x52df0_0x52df2.extracted
