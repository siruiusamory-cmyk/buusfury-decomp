	CODE16
|sub_0800A78E|
	LSR      r7, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	BMI      |loc_0800A760|
	LSR      r4, r0, #0x20
	BEQ      |loc_0800A72C|
	LSR      r4, r0, #0x20
|unk_0800A79C|
	INCBIN	baserom.gba_0xa79c_0xa79e.extracted
|dat_0800A79E|
	DCW      0x0804