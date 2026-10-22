	CODE16
|unk_08054A4C|
	CODE32
|arm_08054A4C|
	TST      r0, #64, 16
	BEQ      |arm_08054850|
	AND      r2, ip, #0x4f
	CMP      r2, #0x48
	BNE      |arm_08054E78|
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08054A64|
