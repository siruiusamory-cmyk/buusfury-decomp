	CODE16
|sub_08052188|
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
	BEQ      |loc_080521A8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080521A8|
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	STMIA    r1!, {r4, r6}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080521C6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080521C6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080521DE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080521DE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080521F6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080521F6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_0805220E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805220E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052226|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052226|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0xd378
	CMP      r5, #0
	BEQ      |loc_0805223E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805223E|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805224E|
	BL       |GBARam_Free|
|loc_0805224E|
	POP      {r3, pc}
|sub_08052250|
|unk_08052250|
	INCBIN	baserom.gba_0x52250_0x52252.extracted
|sub_08052252|
	DCW      0x0804
