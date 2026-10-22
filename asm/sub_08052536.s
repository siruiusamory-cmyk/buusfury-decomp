	CODE16
|sub_08052536|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052552|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052552|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052560|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052560|
	POP      {r3, r4, r5, pc}
|loc_08052562|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x96e0,0x0871,0xe454
|loc_08052572|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805258E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805258E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0805259C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805259C|
	POP      {r3, r4, r5, pc}
|loc_0805259E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x93cc,0x0875,0xe454
|loc_080525AE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0xeadc
	CMP      r5, #0
	BEQ      |loc_080525C6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080525C6|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0xeadc
	CMP      r5, #0
	BEQ      |loc_080525DE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080525DE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0xb1
	LDR      r0, [r0]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_080525FA|
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_080525FA|
	MOV      r0, #0xff
	ADD      r0, #0x8d
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |loc_08052610|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08052610|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeadc
	CMP      r5, #0
	BEQ      |loc_08052622|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052622|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805263E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805263E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0805264C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805264C|
	POP      {r3, r4, r5, pc}
|loc_0805264E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x04cc,0x0875,0xe454
|loc_0805265E|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805266E|
	BL       |GBARam_Free|
|loc_0805266E|
	POP      {r3, pc}
|sub_08052670|
|unk_08052670|
	INCBIN	baserom.gba_0x52670_0x52672.extracted
