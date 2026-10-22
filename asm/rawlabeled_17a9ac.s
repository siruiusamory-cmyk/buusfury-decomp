; PATH-100-006 / R-RAW-001: the census run 0x0817a9ac..0x0817b1b0 as LABELED RAW DATA.

	EXPORT	|unk_0817A9AC|
|unk_0817A9AC|
; cited by 0x082816CE

	INCBIN	build\animframe\gen_17a9ac_17aaac.bin
	EXPORT	|unk_0817AAAC|
|unk_0817AAAC|
; cited by 0x082945AC

	INCBIN	build\animframe\gen_17aaac_17abac.bin
	EXPORT	|unk_0817ABAC|
|unk_0817ABAC|
; cited by 0x082918E8

	INCBIN	build\animframe\gen_17abac_17aca4.bin
	EXPORT	|unk_0817ACA4|
|unk_0817ACA4|
; cited by 0x082945A4 ldm r0 +0x0

	INCBIN	build\animframe\gen_17aca4_17ada4.bin
	EXPORT	|unk_0817ADA4|
|unk_0817ADA4|
; cited by 0x082848E6

	INCBIN	build\animframe\gen_17ada4_17aea4.bin
	EXPORT	|unk_0817AEA4|
|unk_0817AEA4|
; cited by 0x08276D28

	INCBIN	build\animframe\gen_17aea4_17afa4.bin
	EXPORT	|unk_0817AFA4|
|unk_0817AFA4|
; cited by 0x0827EF78


	INCBIN  build\animframe\gen_17afa4_17b09c.bin
|map_anim_row_0817B09C|
|unk_0817B09C|
	DCB 0x10,0x0b
	DCW 0x0375
	DCD 0x0817a9ac,0x0817aaac,0x0817abac,0x0817aca4,0x0817a9ac,0x0817aaac,0x0817ada4,0x0817aaac
	DCD 0x0817aea4,0x0817aaac,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4,0x0817afa4,0x0817aca4
|unk_0817B0E0|
	INCBIN  build\animframe\gen_17b0e0_17b19c.bin
|map_anim_row_0817B19C|
|unk_0817B19C|
	DCB 0x02,0x03
	DCW 0x0372
	DCD 0x0817b0e0,0x0817b140
|unk_0817B1A8|
	INCBIN  baserom.gba_0x17b1a8_0x17b1b0.extracted
