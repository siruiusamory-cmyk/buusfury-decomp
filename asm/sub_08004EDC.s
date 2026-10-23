	CODE16
|sub_08004EDC|
	PUSH     {r3, lr}
	SUB      r1, #4
	LDR      r2, [r1]
	MOV      r1, #1
	STRB     r1, [r2, #1]
	CMP      r0, #0
	BEQ      |loc_08004EF6|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08004EF6|
	POP      {r3, pc}
|loc_08004EF8|
	DCW      0x9354
	DCW      0x0804,0x5620,0x0805,0x0040,0x0600,0xf800
|loc_08004F06|
	LSL      r0, r0, #0x18
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	MOV      r0, #0x48
	LSL      r0, r0, #0
	LSL      r3, r2, #1
	LSL      r0, r0, #0x10
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	LSL      r0, r2, #1
	LSL      r0, r0, #0x10
