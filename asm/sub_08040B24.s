	CODE16
|sub_08040B24|
	PUSH     {lr}
	ADD      r3, r1, #0
	LSL      r0, r0, #0x10
	LSR      r2, r0, #0x10
	LDR      r0, [pc, #0x1c]
	LDR      r0, [r0]
	LDR      r1, [r0]
	MOV      r0, #0x80
	LSL      r0, r0, #2
	CMP      r1, r0
	BEQ      |loc_08040B50|
	ADD      r0, r2, #0
	ADD      r1, r3, #0
	MOV      r2, #0
	BL       |loc_0804092C|
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	B        |loc_08040B52|
	LSL      r0, r0, #0
	STRH     r0, [r7, r3]
	LSL      r0, r0, #0xc
|loc_08040B50|
	LDR      r0, [pc, #4]
|loc_08040B52|
	POP      {r1}
	BX       r1
|loc_08040B56|
	DCW      0x0000
	DCW      0x8080,0x0000
