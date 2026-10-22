	CODE16
|sub_080187D4|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #7
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r0, [r4, #8]
	POP      {r4, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #7
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0801881C|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #7
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r0, [r4, #8]
|loc_0801881C|
	MOV      r0, #1
	POP      {r4, pc}
	MOV      r2, #0xff
	ADD      r2, #0xc9
	MOV      r0, #0
	STR      r0, [r2, r1]
	LDR      r0, [pc, #0x2c]
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r0, [r0, #4]
	ADD      r1, r1, r2
	STR      r0, [r1, #0x10]
	BX       lr
|sub_08018836|
|unk_08018836|
	INCBIN	baserom.gba_0x18836_0x1883a.extracted
