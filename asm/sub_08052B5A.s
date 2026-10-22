	CODE16
|sub_08052B5A|
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x10a28
	CMP      r5, #0
	BEQ      |loc_08052B76|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052B76|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052B8E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052B8E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052BA6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052BA6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052BBE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052BBE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052BD6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052BD6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052BEE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052BEE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052C06|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052C06|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052C1E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052C1E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052C36|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052C36|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052C52|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052C52|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052C60|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052C60|
	POP      {r3, r4, r5, pc}
|loc_08052C62|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe0dc,0x0876,0xe454
|loc_08052C72|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x10a28
	CMP      r5, #0
	BEQ      |loc_08052C8A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052C8A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052CA2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052CA2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052CBA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052CBA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08052CD2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052CD2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052CE2|
	BL       |GBARam_Free|
|loc_08052CE2|
	POP      {r3, pc}
|sub_08052CE4|
|unk_08052CE4|
	INCBIN	baserom.gba_0x52ce4_0x52ce6.extracted
