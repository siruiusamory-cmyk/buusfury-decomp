	CODE16
|sub_08046CAA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |loc_08047A08|
	ADD      sp, #4
	POP      {r3}
	BX       r3
|sub_08046CBA|
|unk_08046CBA|
	INCBIN	baserom.gba_0x46cba_0x46cbc.extracted
