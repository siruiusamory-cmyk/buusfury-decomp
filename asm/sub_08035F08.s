	CODE16
|sub_08035F08|
	PUSH     {r4, r5, lr}
	LDR      r4, [pc, #0x78]
	SUB      sp, #0xc
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r5, #1
	LSL      r5, r5, #0xc
	CMP      r0, r5
	BLT      |loc_08035F34|
	MOV      r0, #0xc8
	STR      r0, [sp, #4]
	MOV      r0, #0x88
	STR      r0, [sp, #8]
	MOV      r0, #0
	ADD      r1, sp, #4
	BL       |loc_08036A44|
	ADD      r1, r0, #0
	LDR      r0, [r4]
|loc_08035F30|
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08035F34|
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	CMP      r0, r5
	BLT      |loc_08035F58|
	MOV      r0, #0x70
	STR      r0, [sp, #4]
	MOV      r0, #0xff
	ADD      r0, #0x11
	STR      r0, [sp, #8]
	MOV      r0, #0
	ADD      r1, sp, #4
	BL       |loc_08036A44|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08035F58|
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	CMP      r0, r5
	BLT      |loc_08035F7C|
	MOV      r0, #0xff
	ADD      r0, #0x29
	STR      r0, [sp, #4]
	MOV      r0, #0xf0
	STR      r0, [sp, #8]
	MOV      r0, #0
	ADD      r1, sp, #4
	BL       |loc_08036A44|
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08035F7C|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
|sub_08035F80|
|unk_08035F80|
	INCBIN	baserom.gba_0x35f80_0x35f86.extracted
