	CODE16
|sub_08050750|
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_0805075C|
	MOV      r0, #8
	BL       |GBARam_Malloc|
|loc_0805075C|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_0805076C|
	MOV      r0, #8
	BL       |GBARam_Malloc|
|loc_0805076C|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08050782|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0805078E|
|loc_08050782|
	LDR      r1, [r4]
	STR      r1, [r0]
	LDR      r2, [r4, #4]
	STR      r2, [r0, #4]
	LDR      r2, [r4, #8]
	STR      r2, [r0, #8]
|loc_0805078E|
	POP      {r4, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BNE      |loc_0805079C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
|loc_0805079C|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r5, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r6, [sp, #0x28]
	BNE      |sub_080507BE|
	MOV      r0, #0x34
|loc_080507B0|
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080507BE|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
