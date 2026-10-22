	CODE16
|unk_08054A24|
	CODE32
|arm_08054A24|
	MOV      r3, #128, 16
	ADD      r2, r3, r0, lsl #1
	ADD      r3, r3, r1, lsl #1
	CMN      r2, #128, 16
	CMNLS    r3, #128, 16
	BHI      |arm_08054850|
	CMP      r2, #128, 16
	MOVHS    r0, r1
	B        |arm_08054E78|
	CODE16
	CODE16
	EXPORT |sub_08054A48|
