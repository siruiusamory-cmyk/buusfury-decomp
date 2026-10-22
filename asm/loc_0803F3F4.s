	CODE16
|loc_0803F3F4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LSL      r0, r1, #0x1f
	BPL      |loc_0803F41E|
	LDRH     r0, [r4, #0x38]
	LSL      r0, r0, #0x1f
	BPL      |loc_0803F40A|
	MOV      r0, #0x64
	STR      r0, [r4, #0x3c]
	B        |loc_0803F41E|
|loc_0803F40A|
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	LDRB     r0, [r0, #6]
	SUB      r0, #0xa0
	BPL      |loc_0803F416|
	ADD      r0, #0xe3
|loc_0803F416|
	LDR      r3, [pc, #0x28]
	MUL      r0, r3
	ASR      r0, r0, #0x10
	STR      r0, [r4, #0x3c]
|loc_0803F41E|
	MOV      r0, #0
	STRH     r0, [r4, #0x38]
|loc_0803F422|
	SWI      2
	MOV      r3, #0x38
	LDRSH    r0, [r4, r3]
	AND      r0, r5
	BEQ      |loc_0803F422|
	LDRH     r0, [r4, #0x38]
	BIC      r0, r5
	STRH     r0, [r4, #0x38]
	POP      {r3, r4, r5, pc}
|loc_0803F434|
	DCW      0x0b6c
	DCW      0x0300,0x7fc0,0x0300,0x0200,0x0400,0x70e4,0x0000
