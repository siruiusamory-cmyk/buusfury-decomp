	CODE16
|sub_0801984E|
	MOV      r1, #0x10
	STR      r1, [r0, #0x4c]
	LDR      r1, [pc, #0x2a4]
	STR      r1, [r0, #0x18]
	BX       lr
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x290]
	ADD      r7, r1, #0
	ADD      r6, r0, #0
	ADD      r5, r2, #0
	SUB      r4, #0xc
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #0xff
	ADD      r1, #1
	CMP      r0, r1
	BLT      |loc_08019886|
	ADD      r3, r5, #0
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	MOV      r0, #0
|unk_0801987A|
	INCBIN	baserom.gba_0x1987a_0x1987c.extracted
|loc_0801987C|
|unk_0801987C|
	INCBIN	baserom.gba_0x1987c_0x1987e.extracted
	ADD      r1, r0, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08019886|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x260]
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x54]
	MOV      r5, #0
	SUB      r6, #0xc
	CMP      r0, #0
	SUB      sp, #0x34
	LDR      r7, [pc, #0x25c]
	BEQ      |loc_080198EC|
	LDR      r0, [r4, #0x58]
	CMP      r0, #0
	BEQ      |sub_080198E4|
	LDR      r0, [r4, #0x60]
	CMP      r0, #0
	BEQ      |loc_080198D8|
	LDR      r0, [r4, #0x20]
	LDR      r1, [r4, #0x24]
	ASR      r0, r0, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #0x30]
	STR      r0, [sp, #0x2c]
	LDR      r5, [r4, #0x60]
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #0xff
	ADD      r1, #1
	CMP      r0, r1
	BLT      |loc_080198D8|
	MOV      r3, #2
	ADD      r2, r5, #0
	MOV      r0, #0
	ADD      r1, sp, #0x2c
	BL       |loc_080197B4|
	ADD      r1, r0, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_080198D8|
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
