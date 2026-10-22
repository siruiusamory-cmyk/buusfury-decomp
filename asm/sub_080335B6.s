	CODE16
|sub_080335B6|
	LSR      r5, r6, #1
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_080335D4|
	MOV      r0, #0x48
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080335D4|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080335D4|
	LDR      r0, [pc, #0x264]
	MOV      r2, #0x40
	STR      r0, [r4]
	ADD      r0, r4, #0
	ADD      r0, #0x14
	MOV      r1, #0xf0
	ADD      r5, r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x258]
	MOV      r2, #1
	STR      r0, [r4, #0x10]
	MOV      r0, #0x90
	STR      r0, [r4, #4]
	MOV      r0, #0
	STR      r0, [r4, #8]
	STR      r6, [r4, #0xc]
	MOV      r0, #2
	STRB     r0, [r4, #0x17]
	LDR      r1, [pc, #0x248]
	STRB     r2, [r5, #2]
	STR      r1, [r5, #0x20]
	STRB     r2, [r4, #0x14]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x230]
	ADD      r5, r1, #0
	STR      r0, [r4]
	ADD      r0, r4, #0
	MOV      r1, #0
	ADD      r0, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x22c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08033628|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08033628|
	POP      {r3, r4, r5, pc}
