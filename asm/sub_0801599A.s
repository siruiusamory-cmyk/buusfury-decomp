	CODE16
|sub_0801599A|
	LSR      r4, r0, #0x20
|loc_0801599C|
	PUSH     {r4}
	LDR      r2, [r0, #8]
	CMP      r2, #0
	BEQ      |loc_080159D8|
	LDR      r0, [r1, #4]
	ADD      r2, #0xff
	ADD      r4, r0, #0
	ADD      r4, #0xff
	ADD      r4, #0x81
	ADD      r2, #0x81
	LDR      r1, [r2, #0x20]
	LDR      r3, [r4, #0x20]
	LDR      r2, [r2, #0x24]
	SUB      r1, r1, r3
	LDR      r3, [r4, #0x24]
	SUB      r2, r2, r3
	ADD      r3, r1, #0
	CMP      r1, #0
	BGE      |loc_080159C4|
|unk_080159C2|
	INCBIN	baserom.gba_0x159c2_0x159c4.extracted
