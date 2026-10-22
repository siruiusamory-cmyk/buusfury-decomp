	CODE16
|sub_08040AF0|
	ADD      r0, r6, #1
	LSL      r0, r0, #0x18
	LSR      r6, r0, #0x18
	CMP      r6, #2
	BHI      |loc_08040B1A|
	ADD      r0, r4, #0
	ADD      r1, r5, #0
	BL       |loc_08040918|
	LSL      r0, r0, #0x10
	LSR      r2, r0, #0x10
	CMP      r2, #0
	BNE      |sub_08040AF0|
	ADD      r0, r4, #0
	ADD      r1, r5, #0
	BL       |loc_08040A8C|
	LSL      r0, r0, #0x10
	LSR      r2, r0, #0x10
	CMP      r2, #0
	BNE      |sub_08040AF0|
|loc_08040B1A|
	ADD      r0, r2, #0
	POP      {r4, r5, r6}
	POP      {r1}
	BX       r1
|sub_08040B22|
|unk_08040B22|
	INCBIN	baserom.gba_0x40b22_0x40b24.extracted
