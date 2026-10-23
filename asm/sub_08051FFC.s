	CODE16
|sub_08051FFC|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052016|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052016|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052024|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052024|
	POP      {r3, r4, r5, pc}
|loc_08052026|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xf080,0x0874,0xe454
|loc_08052036|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052052|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052052|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052060|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052060|
	POP      {r3, r4, r5, pc}
|loc_08052062|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x5098,0x0872,0xe454
|loc_08052072|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805208E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805208E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0805209C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805209C|
	POP      {r3, r4, r5, pc}
|loc_0805209E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x7b64,0x0875,0xe454
|loc_080520AE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080520CA|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080520CA|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080520D8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080520D8|
	POP      {r3, r4, r5, pc}
|loc_080520DA|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xcb00,0x0874,0xe454
|loc_080520EA|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r1, [r4, #0x18]
	MOV      r0, #0
	STR      r0, [r1, #0x18]
	LDR      r0, [pc, #0x24]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x24]
	CMP      r1, r0
	BEQ      |loc_08052110|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052110|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0805211E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805211E|
	POP      {r3, r4, r5, pc}
|loc_08052120|
	DCW      0xc070
	DCW      0x0804,0x9680,0x0804,0xffff,0x0000,0x1c90,0x0807,0xe454
|loc_08052132|
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08052142|
	BL       |GBARam_Free|
|loc_08052142|
	POP      {r3, pc}
|sub_08052144|
|unk_08052144|
	INCBIN	baserom.gba_0x52144_0x52146.extracted
|sub_08052146|
	DCW      0x0804
