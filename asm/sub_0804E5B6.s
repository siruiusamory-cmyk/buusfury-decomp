	CODE16
|sub_0804E5B6|
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x35
	BL       |inc_0x0158_0x143f2|
	LDR      r1, [r0, #4]
	LDR      r0, [r4, #0x38]
	CMP      r0, r1
	BEQ      |loc_0804E5D0|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed74
|loc_0804E5D0|
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
	PUSH     {r4, lr}
	MOV      r0, #0
	STRB     r0, [r1, #0x11]
	STRH     r0, [r1, #0x12]
	ADD      r4, r1, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
|sub_0804E604|
|unk_0804E604|
	INCBIN	baserom.gba_0x4e604_0x4e606.extracted
