	CODE16
|sub_0800C532|
	LDR      r2, [r1]
	ADD      r3, r2, #0
	ADD      r3, #8
|loc_0800C538|
	STR      r3, [r1]
	MOV      r1, #1
	LSL      r1, r1, #0xd
	STR      r1, [r2]
	LDR      r3, [r0, #0x2c]
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r1, r3
	STR      r1, [r2]
	LDR      r0, [r0, #0x30]
	LSR      r1, r1, #8
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	LSL      r1, r1, #8
	ORR      r0, r1
	STR      r0, [r2]
	LDR      r0, [r2, #4]
	MOV      r1, #3
	LSL      r1, r1, #0xa
	ORR      r0, r1
	LDR      r1, [pc, #0x3c]
	LSR      r0, r0, #0xa
	LDRH     r1, [r1, #2]
	LSL      r0, r0, #0xa
	LSL      r1, r1, #0x16
	LSR      r1, r1, #0x16
	ORR      r0, r1
	STR      r0, [r2, #4]
	MOV      r0, #0
	BX       lr
	PUSH     {r3, lr}
	CMP      r1, #0xc
	BNE      |sub_0800C588|
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	POP      {r3, pc}
|sub_0800C588|
|unk_0800C588|
	INCBIN	baserom.gba_0xc588_0xc58a.extracted
|sub_0800C58A|
|unk_0800C58A|
	INCBIN	baserom.gba_0xc58a_0xc58e.extracted
	CMP      r1, #3
	BLT      |sub_0800C596|
	MOV      r0, #2
	BX       lr
