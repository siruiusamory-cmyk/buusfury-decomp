	CODE16
|Thunk_PaletteCopy|
	BX       pc
	MOV      r8, r8
|unk_08049148|
; cited by 0x08049148 (a pc-relative load targets 0x0804914C)
	INCBIN	baserom.gba_0x49148_0x49150.extracted
	CODE16
	EXPORT |sub_08049150|
