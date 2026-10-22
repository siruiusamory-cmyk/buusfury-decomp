	CODE16
|sub_08053334|
	ASR      r0, r4, #0x17
|unk_08053336|
	INCBIN	baserom.gba_0x53336_0x53338.extracted
|sub_08053338|
|unk_08053338|
	INCBIN	baserom.gba_0x53338_0x533c4.extracted
|loc_080533C4|
|unk_080533C4|
; cited by 0x08053078 (a pc-relative load targets 0x080533C8)
	INCBIN	baserom.gba_0x533c4_0x5349c.extracted
|sub_0805349C|
|unk_0805349C|
	INCBIN	baserom.gba_0x5349c_0x534a0.extracted
	LSL      r0, r1, #2
	LSL      r0, r0, #0x10
	BX       pc
	LSL      r0, r0, #0
