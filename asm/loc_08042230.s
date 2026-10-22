	CODE16
|loc_08042230|
	BL       |loc_08041c9a| + 0x4a
	MOV      r0, #3
	STRB     r0, [r4, #6]
|loc_08042238|
	MOV      r0, #1
	POP      {r4, pc}
|sub_0804223C|
|unk_0804223C|
	INCBIN	baserom.gba_0x4223c_0x4223e.extracted
