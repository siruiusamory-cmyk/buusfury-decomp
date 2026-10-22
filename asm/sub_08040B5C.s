	CODE16
|sub_08040B5C|
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r1, #0
	LSL      r0, r0, #0x10
	LSR      r4, r0, #0x10
	MOV      r6, #0
	B        |loc_08040B6E|
|loc_08040B68|
	ADD      r0, r6, #1
	LSL      r0, r0, #0x18
	LSR      r6, r0, #0x18
|loc_08040B6E|
	CMP      r6, #2
	BHI      |loc_08040B92|
	ADD      r0, r4, #0
	ADD      r1, r5, #0
	BL       |sub_08040B24|
	LSL      r0, r0, #0x10
	LSR      r2, r0, #0x10
	CMP      r2, #0
	BNE      |loc_08040B68|
	ADD      r0, r4, #0
	ADD      r1, r5, #0
	BL       |loc_08040A8C|
	LSL      r0, r0, #0x10
	LSR      r2, r0, #0x10
	CMP      r2, #0
	BNE      |loc_08040B68|
|loc_08040B92|
	ADD      r0, r2, #0
	POP      {r4, r5, r6}
	POP      {r1}
	BX       r1
|sub_08040B9A|
|unk_08040B9A|
	INCBIN	baserom.gba_0x40b9a_0x40b9c.extracted
