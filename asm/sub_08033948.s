	CODE16
|sub_08033948|
	MOV      r0, #0xff
	ADD      r0, #0x22
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |loc_08033966|
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_08033966|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xf7fc
	POP      {r3, r4, r5, pc}
|sub_0803396E|
|unk_0803396E|
	INCBIN	baserom.gba_0x3396e_0x33972.extracted
