	CODE16
|sub_08052A24|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052A3E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052A3E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052A4C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052A4C|
	POP      {r3, r4, r5, pc}
|loc_08052A4E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x24ec,0x0807,0xe454
|loc_08052A5E|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052A7A|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052A7A|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052A88|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052A88|
	POP      {r3, r4, r5, pc}
|loc_08052A8A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xe9f8,0x0874,0xe454
|loc_08052A9A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	MOV      r1, #0
	ADD      r4, r0, #0
	ADD      r0, #0x1c
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x24]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052ABE|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052ABE|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052ACC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052ACC|
	POP      {r3, r4, r5, pc}
|loc_08052ACE|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x24d4,0x0807,0xe454
|loc_08052ADE|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052AEE|
	BL       |GBARam_Free|
|loc_08052AEE|
	POP      {r3, pc}
|sub_08052AF0|
|unk_08052AF0|
	INCBIN	baserom.gba_0x52af0_0x52af2.extracted
|sub_08052AF2|
	DCW      0x0804
