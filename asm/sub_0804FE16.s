	CODE16
|sub_0804FE16|
	LSL      r0, r0, #0
	MOV      r4, #0xf8
	LSR      r7, r0, #0x20
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDRB     r0, [r0]
	ADD      r0, #0xff
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r4]
	BNE      |loc_0804FE4A|
	LDRH     r0, [r4, #2]
	LDR      r1, [pc, #0x18]
	CMP      r0, r1
	BEQ      |loc_0804FE4A|
	MOV      r3, #2
	LDR      r0, [pc, #0x14]
	LDRSH    r1, [r4, r3]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
	MOV      r0, #0
	MVN      r0, r0
	STRH     r0, [r4, #2]
|loc_0804FE4A|
	POP      {r4, pc}
|sub_0804FE4C|
|unk_0804FE4C|
	INCBIN	baserom.gba_0x4fe4c_0x4fe4e.extracted
|sub_0804FE4E|
	DCW      0x0000
	DCW      0x25e8
	DCW      0x0807
