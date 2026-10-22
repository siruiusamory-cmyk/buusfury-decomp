	CODE16
|unk_08053954|
	CODE32
|arm_08053954|
	STMDB    sp!, {r4, r5}
	MOV      r5, #64, 18
	CMP      r0, #1
	ADC      r4, r5, r1, lsl #1
	CMP      r2, #1
	ADC      r5, r5, r3, lsl #1
	CMN      r4, #64, 18
	CMNLS    r5, #64, 18
	BHI      |arm_0805398C|
	CMP      r4, #64, 18
	LDMIA    sp!, {r4, r5}
	MOVHS    r1, r3
	MOVHS    r0, r2
	B        |arm_08054E78|
|arm_0805398C|
	LDMIA    sp!, {r4, r5}
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08053994|
