	CODE16
|unk_08053998|
	CODE32
|arm_08053998|
	TST      r1, #128, 20
	BEQ      |arm_08054850|
	AND      r2, ip, #0x4f
	CMP      r2, #0x48
	BNE      |arm_08054E78|
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_080539B0|
