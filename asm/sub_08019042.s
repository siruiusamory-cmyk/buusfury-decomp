	CODE16
|sub_08019042|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0801906A|
|loc_08019052|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #0x10]
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	LDR      r3, [r0, #8]
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r0, [r5, #0xc]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08019052|
|loc_0801906A|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0801906C|
|unk_0801906C|
	INCBIN	baserom.gba_0x1906c_0x1906e.extracted
|sub_0801906E|
	DCW      0x0804
	DCW      0x930c
	DCW      0x0804
