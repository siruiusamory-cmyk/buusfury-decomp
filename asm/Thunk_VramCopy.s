	CODE16
|Thunk_VramCopy|
	BX       pc
	MOV      r8, r8
|unk_0804913C|
; cited by 0x0804913C (a pc-relative load targets 0x08049140)
	INCBIN	baserom.gba_0x4913c_0x49144.extracted
	CODE16
	EXPORT |Thunk_PaletteCopy|
