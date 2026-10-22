	CODE16
|loc_08040048|
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [pc, #0x1d0]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08040076|
	LDR      r1, [r0]
	ADD      r6, r0, #0
	LDR      r2, [r1, #0x10]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5]
	STR      r4, [r0]
	LDR      r1, [r6]
	ADD      r0, r6, #0
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	B        |loc_0804007A|
|loc_08040076|
	LDR      r0, [r5]
	STR      r4, [r0]
|loc_0804007A|
	LDR      r0, [r5]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [pc, #0x194]
	MOV      r0, #0
	STR      r0, [r1, #0x14]
	LDR      r0, [r1, #0x14]
	LDR      r1, [pc, #0x190]
	STR      r0, [r1, #0xc]
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080400A6|
	LDR      r1, [pc, #0x184]
	STR      r1, [r0]
|loc_080400A6|
	BL       |loc_08040048|
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080400BC|
	LDR      r1, [pc, #0x170]
	STR      r1, [r0]
|loc_080400BC|
	BL       |loc_08040048|
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080400D2|
	LDR      r1, [pc, #0x160]
	STR      r1, [r0]
|loc_080400D2|
	BL       |loc_08040048|
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080400E8|
	LDR      r1, [pc, #0x14c]
	STR      r1, [r0]
|loc_080400E8|
	BL       |loc_08040048|
	POP      {r3, pc}
