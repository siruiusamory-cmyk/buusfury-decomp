	CODE16
|sub_0803EA24|
	LSR      r1, r1, #0x1c
	CMP      r1, #0xf
	BNE      |loc_0803EA36|
	AND      r0, r1
	STRB     r0, [r4, #0xb]
	ADD      r0, r5, #0
	BL       |loc_0803E5AC|
	STR      r6, [r5, #0x54]
|loc_0803EA36|
	LDRB     r0, [r4, #0xa]
	MOV      r1, #1
	ORR      r0, r1
	STRB     r0, [r4, #0xa]
	ADD      r0, r5, #0
	BL       |loc_0803E8BC|
	POP      {r4, r5, r6, pc}
|sub_0803EA46|
|unk_0803EA46|
; cited by 0x0803E7CC (a pc-relative load targets 0x0803EA48)
	INCBIN	baserom.gba_0x3ea46_0x3eb1a.extracted
