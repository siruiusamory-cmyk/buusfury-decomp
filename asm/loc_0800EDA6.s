	CODE16
|loc_0800EDA6|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x34]
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x3c]
	CMP      r1, r0
	BEQ      |loc_0800EDBA|
	STR      r0, [r4, #0x34]
	MOV      r0, #0
	STR      r0, [r4, #0x38]
	STR      r0, [r4, #0x30]
|loc_0800EDBA|
	LDR      r0, [r4, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
|loc_0800EDC0|
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x1c]
	SUB      r0, #4
	STR      r0, [r4, #0x18]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
|loc_0800EDDC|
	DCW      0x9680
	DCW      0x0804,0x25e8,0x0807,0xac20,0x0804,0x1ba8,0x0300,0xffff
	DCW      0x0000,0xe454
|loc_0800EDF2|
	LSR      r4, r0, #0x20
	SUB      r0, r0, r4
	LSL      r0, r0, #0xc
