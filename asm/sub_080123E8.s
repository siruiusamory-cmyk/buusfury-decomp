	CODE16
|sub_080123E8|
	PUSH     {r3, lr}
	ADD      r2, r0, #0
	ADD      r2, #8
	ADD      r3, r0, #0
	ADD      r1, #3
	MOV      r0, #0
	BL       |loc_08011F5A|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r2, r0, #0
	ADD      r2, #8
	MOV      r0, #0
	BL       |loc_08011FD6|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r3, #0xc
	LDRB     r2, [r1, #3]
	ADD      r1, #4
	MOV      r0, #0
	BL       |sub_08012012|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r2, r0, #0
	ADD      r2, #0xc
	LDR      r3, [r0, #0x14]
	MOV      r0, #0
	BL       |loc_080121D8|
	POP      {r3, pc}
	ADD      r2, r0, #0
	ADD      r2, #0xc
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_0801227E|
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r2, r0, #0
	ADD      r2, #0xc
	LDR      r3, [r0, #0x14]
	MOV      r0, #0
	BL       |loc_08012334|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r1, #4]
	STR      r1, [r0]
	MOV      r1, #0
	STRH     r1, [r0, #8]
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08012462|
	LDR      r1, [pc, #0x170]
	STR      r1, [r0]
|loc_08012462|
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |sub_0801236E|
	POP      {r3, pc}
