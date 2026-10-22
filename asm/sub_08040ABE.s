	CODE16
|sub_08040ABE|
	ADD      r0, r3, #1
	LSL      r0, r0, #0x18
	LSR      r3, r0, #0x18
	CMP      r3, #3
	BHI      |loc_08040AD8|
	LDRH     r1, [r4]
	LDRH     r0, [r2]
	ADD      r2, #2
	ADD      r4, #2
	CMP      r1, r0
	BEQ      |sub_08040ABE|
	MOV      r5, #0x80
	LSL      r5, r5, #8
|loc_08040AD8|
	ADD      r0, r5, #0
|loc_08040ADA|
	ADD      sp, #8
	POP      {r4, r5}
	POP      {r1}
	BX       r1
|sub_08040AE2|
|unk_08040AE2|
	INCBIN	baserom.gba_0x40ae2_0x40af0.extracted
