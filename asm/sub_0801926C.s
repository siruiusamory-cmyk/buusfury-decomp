	CODE16
|sub_0801926C|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	POP      {r3, pc}
|loc_08019280|
	CMP      r3, #0xa8
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [pc, #0x20]
	LSL      r0, r0, #3
	ADD      r0, r0, r2
	LDR      r0, [r0]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	LDR      r3, [pc, #0xc]
	LSL      r0, r0, #3
	ADD      r0, r0, r3
	LDR      r0, [r0, #4]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
|sub_080192AC|
|unk_080192AC|
	INCBIN	baserom.gba_0x192ac_0x192ae.extracted
