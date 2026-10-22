	CODE16
|loc_08027B8E|
	LDR      r1, [r4, #0xc]
	ADD      r3, r1, #0
	CMP      r1, #0
	BGE      |loc_08027B98|
|unk_08027B96|
	INCBIN	baserom.gba_0x27b96_0x27b98.extracted
