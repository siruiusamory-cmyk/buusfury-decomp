	CODE16
	EXPORT |sub_08046118|
	EXPORT |loc_08046AA0|
	EXPORT |Thunk_JumpRegister1|
	EXPORT |sub_08046AA8|
	EXPORT |sub_08046AAE|
	EXPORT |loc_08046AB6|
	EXPORT |loc_08046AC0|
	EXPORT |loc_08046ACE|
	EXPORT |loc_08046ADC|
	EXPORT |loc_08046AFA|
	EXPORT |loc_08046B08|
	CODE16
|sub_08046118|
	STRB     r0, [r1, #4]
	BL       |loc_08045b40|
	POP      {r7}
	POP      {r3}
	BX       r3
	AREA UnusedGBARam8, CODE, READONLY
	CODE16
|unk_080462AC|
; cited by 0x080462B0 (a pc-relative load targets 0x08046A64)
	INCBIN	baserom.gba_0x462ac_0x46a7a.extracted
	CODE16
|dat_08046A7A|
	DCW      0x0000
	DCW      0xf996
	DCW      0x0000
	DCW      0x500a
	DCW      0x0000
	DCW      0x01ee
	DCW      0x9966
	DCW      0x5002
	DCW      0x0000
	DCW      0x01ee
	DCW      0x0000
	DCW      0x5003
	DCW      0x0000
	DCW      0x0200
	DCW      0x0400
	DCW      0x500b
	DCW      0x0000
	DCW      0x5083
	DCW      0x0000

