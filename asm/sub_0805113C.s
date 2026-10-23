	CODE16
|sub_0805113C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051156|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051156|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051164|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051164|
	POP      {r3, r4, r5, pc}
|loc_08051166|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x96d8,0x0871,0xe454
|loc_08051176|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051192|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051192|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080511A0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080511A0|
	POP      {r3, r4, r5, pc}
|loc_080511A2|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe200,0x0871,0xe454
|loc_080511B2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0xd898
	CMP      r5, #0
	BEQ      |loc_080511CA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080511CA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080511E6|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080511E6|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080511F4|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080511F4|
	POP      {r3, r4, r5, pc}
|loc_080511F6|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe228,0x0871,0xe454
|loc_08051206|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	MOV      r1, #0
	ADD      r4, r0, #0
	ADD      r0, #0x10
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x24]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805122A|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805122A|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051238|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051238|
	POP      {r3, r4, r5, pc}
|loc_0805123A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x7398,0x0875,0xe454
|loc_0805124A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051262|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051262|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08051272|
	BL       |GBARam_Free|
|loc_08051272|
	POP      {r3, pc}
|sub_08051274|
|unk_08051274|
	INCBIN	baserom.gba_0x51274_0x51276.extracted
|sub_08051276|
	DCW      0x0804
