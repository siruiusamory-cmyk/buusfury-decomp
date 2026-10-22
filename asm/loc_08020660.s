	CODE16
|loc_08020660|
	LDR      r1, [r4, #0x10]
	ADD      r3, r1, #0
	CMP      r1, #0
	BGE      |loc_0802066A|
|unk_08020668|
	INCBIN	baserom.gba_0x20668_0x2066a.extracted
