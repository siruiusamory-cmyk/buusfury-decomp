	CODE16
|Battle_ApplyDamage|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	MOV      r0, #0xa3
	LSL      r0, r0, #2
	ADD      r5, r4, r0
	LDR      r0, [r5]
	MOV      r7, #0
	ADD      r6, r1, #0
	CMP      r0, #0
	BNE      |loc_0800FA42|
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|loc_0800FA42|
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |loc_0800E8E6|
	LDR      r1, [r5]
	LDR      r0, [r6, #0x18]
	SUB      r0, r1, r0
	STR      r0, [r5]
	CMP      r0, #0
	BGT      |loc_0800FA7C|
	LDR      r0, [pc, #0x288]
	ADD      r2, r4, #0
	STR      r7, [r5]
	LDR      r0, [r0]
	MOV      r1, #0x11
	BL       |loc_08011C0C|
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x24]
	ADD      r2, r6, #0
	LDR      r0, [r0, #0x14]
	ADD      r1, r4, #0
	LDR      r3, [r0, #8]
	BL       |inc_0x046118_0x049114| + 0x98e
	MOV      r0, #1
	B        |inc_0x0158_0x143f2| + 0xf8e8
|loc_0800FA7C|
	MOV      r0, #0
	B        |inc_0x0158_0x143f2| + 0xf8e8
