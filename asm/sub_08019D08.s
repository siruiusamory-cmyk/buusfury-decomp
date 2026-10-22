	CODE16
|sub_08019D08|
|unk_08019D08|
; cited by 0x08019B08 (a pc-relative load targets 0x08019D0C)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x19d0c_0x19d1e.extracted
|sub_08019D1E|
|unk_08019D1E|
	INCBIN	baserom.gba_0x19d1e_0x19d22.extracted
	LSL      r1, r0, #0x18
	MOV      r0, #0
	BX       lr
|sub_08019D28|
|unk_08019D28|
	INCBIN	baserom.gba_0x19d28_0x19d2a.extracted
