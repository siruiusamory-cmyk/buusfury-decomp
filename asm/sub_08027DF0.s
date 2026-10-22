	CODE16
|sub_08027DF0|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x50]
	LDR      r1, [r0, #4]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x11d3c
|loc_08027E04|
	ADD      r0, r4, #0
	BEQ      |loc_08027E14|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08027E14|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x1c]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11458
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x10]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11426
	LDR      r0, [r4, #4]
	LDR      r0, [r0, #0x10]
	POP      {r4, pc}
|sub_08027E40|
|unk_08027E40|
	INCBIN	baserom.gba_0x27e40_0x27e42.extracted
