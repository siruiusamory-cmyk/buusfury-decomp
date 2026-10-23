	CODE16
|sub_0804776C|
	ADD      r0, #0
|unk_0804776E|
	INCBIN	baserom.gba_0x4776e_0x47770.extracted
|sub_08047770|
|unk_08047770|
; cited by 0x080477B8 (a pc-relative load targets 0x080477CC)
	INCBIN	baserom.gba_0x47770_0x479fc.extracted
|sub_080479FC|
|unk_080479FC|
	INCBIN	baserom.gba_0x479fc_0x47a00.extracted
	CODE16
|dat_08047A00|
	DCW      0x4070
|unk_08047A02|
	INCBIN	baserom.gba_0x47a02_0x47a08.extracted

