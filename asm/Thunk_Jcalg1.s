	IMPORT |GBARam_Free|
	IMPORT |GBARam_Malloc|
	IMPORT |inc_0x071c90_0x3715c0|
	CODE16
	EXPORT |Thunk_Jcalg1|
|Thunk_Jcalg1|
	BX       pc
	MOV      r8, r8
|unk_08049124|
; cited by 0x08049124 (a pc-relative load targets 0x08049128)
	INCBIN	baserom.gba_0x49124_0x4912c.extracted
	CODE16
	EXPORT |sub_0804912C|
	CODE16
|sub_0804912C|
	BX       pc
	MOV      r8, r8
|unk_08049130|
; cited by 0x08049130 (a pc-relative load targets 0x08049134)
	INCBIN	baserom.gba_0x49130_0x49138.extracted
	CODE16
	EXPORT |Thunk_VramCopy|
