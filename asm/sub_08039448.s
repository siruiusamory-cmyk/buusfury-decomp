	CODE16
|sub_08039448|
	PUSH     {r4, lr}
	LDR      r4, [r1, #0x30]
	MOV      r0, #8
	BL       |inc_0x03d784_0x041118| + 0x2348
	CMP      r4, #0
	BEQ      |loc_0803946E|
	MOV      r2, #1
	LSL      r2, r2, #9
|loc_0803945A|
	ADD      r0, #1
	ADD      r3, r4, r2
	LSL      r1, r0, #0x1d
	LSR      r1, r1, #0x1d
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r1, [r3, #4]
	LDR      r4, [r4, #0x38]
	CMP      r4, #0
	BNE      |loc_0803945A|
|loc_0803946E|
	MOV      r0, #1
	POP      {r4, pc}
|sub_08039472|
|unk_08039472|
	INCBIN	baserom.gba_0x39472_0x39476.extracted
|sub_08039476|
	DCW      0x0000
	DCW      0x32b0
	DCW      0x0300
	DCW      0x2201
	DCW      0x02d2
