	CODE16
|sub_080501E2|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |inc_0x03d784_0x041118| + 0x377e
	LDR      r1, [pc, #8]
	LDR      r0, [r1, #0x14]
	ADD      r0, #1
	STR      r0, [r1, #0x14]
	POP      {r3, pc}
|loc_080501F4|
	DCW      0x4a6c
	DCW      0x0300,0x4770
|loc_080501FA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |inc_0x042118_0x043118| + 0xc6c
	LDR      r1, [pc, #8]
	LDR      r0, [r1, #0x14]
	ADD      r0, #1
	STR      r0, [r1, #0x14]
	POP      {r3, pc}
|sub_0805020C|
|unk_0805020C|
	INCBIN	baserom.gba_0x5020c_0x5020e.extracted
