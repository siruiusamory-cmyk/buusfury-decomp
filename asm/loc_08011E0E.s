	CODE16
|loc_08011E0E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r7, #0x61
	ADD      r4, r0, #0
	LSL      r7, r7, #4
	ADD      r2, r4, r7
	MOV      r3, #0x2f
	LSL      r3, r3, #6
	LDR      r1, [r2]
	ADD      r5, r4, r3
	MOV      r0, #0
	CMP      r1, #0
	BLE      |loc_08011E48|
|loc_08011E26|
	MOV      r7, #0x61
	LSL      r3, r0, #2
	LDR      r1, [r5, #0x38]
	ADD      r3, r3, r2
	LSL      r7, r7, #4
	ADD      r1, r1, r7
	LDR      r6, [r3, #4]
	LDR      r3, [r1]
	ADD      r0, #1
	ADD      r7, r3, #1
	STR      r7, [r1]
	LSL      r3, r3, #2
	ADD      r1, r3, r1
	STR      r6, [r1, #4]
	LDR      r1, [r2]
	CMP      r1, r0
	BGT      |loc_08011E26|
|loc_08011E48|
	MOV      r0, #0
	STR      r0, [r2]
	ADD      r0, r4, #0
	BL       |loc_08011B04|
	LDR      r6, [r5, #0x38]
	MOV      r2, #7
	LSL      r2, r2, #9
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x046118_0x049114| + 0xcb8
	ADD      r0, r6, #0
	BL       |GBARam_Free|
	LDR      r0, [pc, #0xac]
	LDR      r2, [pc, #0xac]
	LDR      r0, [r0, #4]
	LDR      r1, [r5, #0x3c]
	ADD      r0, r0, r2
	BL       |sub_0803E4A0|
	MOV      r2, #0
	MOV      r1, #0xb
	ADD      r0, r4, #0
	BL       |loc_08011C0C|
	POP      {r3, r4, r5, r6, r7, pc}
	LSR      r1, r0, #0x1e
	LSR      r0, r0, #0xc
	MOV      r2, #0xc
	AND      r0, r2
	ORR      r0, r1
	LDR      r1, [pc, #0x88]
	LSL      r0, r0, #3
	ADD      r1, #0xc
	ADD      r0, r0, r1
	BX       lr
