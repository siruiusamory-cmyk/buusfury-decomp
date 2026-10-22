	CODE16
|Object_Construct8|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r2, #0
	MOV      r1, #0xa
	BL       |loc_08011C0C|
	ADD      r0, r4, #0
	BL       |loc_08011D36|
	LDR      r0, [pc, #0x14c]
	LDR      r1, [pc, #0x14c]
	LDR      r0, [r0, #4]
	ADD      r0, r0, r1
	BL       |sub_0803E44C|
	MOV      r1, #0x2f
	LSL      r1, r1, #6
	ADD      r6, r4, r1
	MOV      r7, #7
	LSL      r7, r7, #9
	STR      r0, [r6, #0x3c]
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BEQ      |loc_08011DF2|
	ADD      r2, r7, #0
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0xcb8
|loc_08011DF2|
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r1, r4, r0
	MOV      r0, #0
	STR      r5, [r6, #0x38]
	STR      r0, [r1]
	LDR      r1, [pc, #0x11c]
	STR      r0, [r4, #4]
	ADD      r1, r4, r1
	STR      r0, [r1]
	ADD      r0, r4, #0
	BL       |loc_08011B04|
	POP      {r3, r4, r5, r6, r7, pc}
