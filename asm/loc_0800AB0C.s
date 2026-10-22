	CODE16
|loc_0800AB0C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |List_ReleaseAll1|
	LDR      r1, [r4, #4]
	ADD      r0, r4, #4
	LSL      r1, r1, #3
	ADD      r0, r1, r0
	SUB      r0, #4
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	LDR      r1, [r4]
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |List_ReleaseAll1|
	LDR      r1, [r4, #4]
	ADD      r0, r4, #4
	LSL      r1, r1, #3
	ADD      r0, r1, r0
	LDR      r0, [r0]
	LDR      r1, [r4]
	LDR      r0, [r0, #4]
	ADD      r2, r5, #0
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, pc}
|sub_0800AB50|
|unk_0800AB50|
	INCBIN	baserom.gba_0xab50_0xab52.extracted
