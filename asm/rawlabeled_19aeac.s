; PATH-100-006 / R-RAW-001: the census run 0x0819aeac..0x0819b178 as LABELED RAW DATA.

	EXPORT	|unk_0819AEAC|
|unk_0819AEAC|
; cited by 0x081C5ED0

	INCBIN  build\animframe\gen_19aeac_19b098.bin
|map_anim_row_0819B098|
|unk_0819B098|
	DCB 0x04,0x0c
	DCW 0x0374
	DCD 0x0819aeac,0x0819af5c,0x0819aff8,0x0819af5c
	EXPORT	|unk_0819B0AC|
|unk_0819B0AC|
; cited by 0x081BFA38

	INCBIN	build\animframe\gen_19b0ac_19b104.bin
	EXPORT	|unk_0819B104|
|unk_0819B104|
; cited by 0x082779B2 ldrh r0 +0xc str r0 +0x58

	INCBIN	build\animframe\gen_19b104_19b130.bin
	EXPORT	|unk_0819B130|
|unk_0819B130|
; cited by 0x08285B06


	INCBIN  build\animframe\gen_19b130_19b15c.bin
|map_anim_row_0819B15C|
|unk_0819B15C|
	DCB 0x04,0x03
	DCW 0x0371
	DCD 0x0819b0ac,0x0819b0d8,0x0819b104,0x0819b130
|unk_0819B170|
	INCBIN  baserom.gba_0x19b170_0x19b178.extracted
