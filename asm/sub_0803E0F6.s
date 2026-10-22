	CODE16
|sub_0803E0F6|
	LSL      r2, r1, #0x1c
	BPL      |loc_0803E114|
	LDR      r2, [r0, #0x28]
	LDR      r3, [r2]
	STR      r3, [r0, #8]
	LDRH     r3, [r2, #6]
	LSL      r3, r3, #0xe
	STR      r3, [r0, #0x20]
	LDRH     r3, [r2, #8]
	LSL      r3, r3, #0xe
	STR      r3, [r0, #0x24]
	LDRH     r3, [r2, #0xa]
	STRH     r3, [r0, #0x14]
	LDRB     r2, [r2, #4]
	STRB     r2, [r0, #0x11]
|loc_0803E114|
	LSL      r2, r1, #0x1d
	BPL      |loc_0803E124|
	MOV      r2, #0
	STR      r2, [r0]
	LDRB     r2, [r0, #0x11]
	MOV      r3, #4
	BIC      r2, r3
	STRB     r2, [r0, #0x11]
|loc_0803E124|
	LSL      r1, r1, #0x1e
	BPL      |loc_0803E14A|
	LDRH     r2, [r0, #0x14]
	LDR      r1, [r0, #0x30]
	LDR      r3, [pc, #0x240]
	MUL      r1, r2
	LSR      r1, r1, #0xe
	LDR      r2, [pc, #0x240]
	MUL      r1, r3
	ADD      r1, r1, r2
	LSR      r1, r1, #0xc
	STR      r1, [r0, #0x1c]
	LDRB     r2, [r0, #0x11]
	LSL      r2, r2, #0x1d
	BPL      |loc_0803E148|
|unk_0803E142|
	INCBIN	baserom.gba_0x3e142_0x3e144.extracted
	STR      r1, [r0, #4]
	B        |loc_0803E14A|
|loc_0803E148|
	STR      r1, [r0, #4]
|loc_0803E14A|
	MOV      r1, #1
	STRB     r1, [r0, #0x10]
|loc_0803E14E|
	POP      {r4}
	BX       lr
