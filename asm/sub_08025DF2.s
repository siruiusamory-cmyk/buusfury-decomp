	CODE16
|sub_08025DF2|
	LSL      r0, r0, #0
	DCW      0xf000,0x0600
	MOV      r0, #0xc
	LSL      r0, r0, #0
	MOV      r0, #0x4c
	LSL      r0, r0, #0
	LSL      r0, r3, #0
	LSL      r0, r0, #0x10
	MOV      r3, #0x60
	LSR      r3, r6, #1
	STRH     r4, [r5]
	LSL      r0, r0, #0
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x2c]
	ASR      r0, r0, #1
	BX       lr
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x30]
	ASR      r0, r0, #1
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #0
	BL       |loc_080261D4|
	POP      {r3, pc}
	PUSH     {r4, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08025E3E|
	ADD      r0, r4, #0
	POP      {r4, pc}
|loc_08025E3E|
	ADD      r0, r4, #0
	BL       |loc_08024A7C|
	LDR      r0, [pc, #4]
	STR      r0, [r4]
	ADD      r0, r4, #0
	POP      {r4, pc}
|sub_08025E4C|
|unk_08025E4C|
	INCBIN	baserom.gba_0x25e4c_0x25e4e.extracted
