	CODE16
|sub_0804E54E|
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x31
	BL       |inc_0x0158_0x143f2|
	LDR      r1, [r0, #4]
	LDR      r0, [r4, #0x38]
	CMP      r0, r1
	BEQ      |loc_0804E568|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed74
|loc_0804E568|
	POP      {r4, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x32
	BL       |inc_0x0158_0x143f2|
	LDR      r1, [r0, #4]
	LDR      r0, [r4, #0x38]
	CMP      r0, r1
	BEQ      |loc_0804E584|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed74
|loc_0804E584|
	MOV      r1, #0xc
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1, #0x58]
	ADD      r1, #0x4c
	LDR      r1, [r1, #0x54]
	LDR      r2, [r0, #0x50]
	CMP      r1, r2
	BNE      |loc_0804E5B2|
	LDR      r1, [pc, #4]
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0804E5B2|
	POP      {r3, pc}
|sub_0804E5B4|
|unk_0804E5B4|
	INCBIN	baserom.gba_0x4e5b4_0x4e5b6.extracted
