	CODE16
|loc_080192BA|
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |loc_080192CA|
|loc_080192C0|
	LDR      r1, [r1]
	ADD      r1, #4
	LDR      r2, [r1]
	CMP      r2, #0
	BNE      |loc_080192C0|
|loc_080192CA|
	STR      r0, [r1]
	BX       lr
