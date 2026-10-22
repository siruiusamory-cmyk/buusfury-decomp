	CODE16
|sub_080094B8|
	PUSH     {r4}
	LDR      r2, [r1]
	STR      r2, [r0]
	LDR      r4, [r1, #4]
	ADD      r2, r1, #4
	STR      r4, [r0, #4]
	LDR      r1, [r1]
	LDR      r2, [r2]
	ASR      r1, r1, #0xa
	STR      r1, [r0, #0x18]
	ASR      r2, r2, #0xa
	STR      r2, [r0, #0x1c]
	ADD      r1, #0xf0
	STR      r1, [r0, #0x20]
	ADD      r2, #0xa0
	STR      r2, [r0, #0x24]
	LDR      r1, [r0]
	LDR      r2, [r0, #0x30]
	ADD      r1, r1, r2
	ASR      r1, r1, #0xa
	STR      r1, [r0, #0x28]
	LDR      r1, [r0, #4]
	LDR      r2, [r0, #0x34]
	ADD      r1, r1, r2
	ASR      r1, r1, #0xa
	STR      r1, [r0, #0x2c]
	POP      {r4}
	BX       lr
