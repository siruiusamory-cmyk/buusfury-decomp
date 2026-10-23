	CODE16
|sub_080123C0|
|unk_080123C0|
; cited by 0x080121E6 (a pc-relative load targets 0x080123C4)
		MOV r0, #0
		POP {r4, pc}
	INCBIN  baserom.gba_0x123c4_0x123de.extracted
|sub_080123DE|
	DCW      0x0804
	DCW      0xa7c4
	DCW      0x0804
	DCW      0x2890
	DCW      0x0807
