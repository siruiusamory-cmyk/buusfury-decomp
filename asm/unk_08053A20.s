	CODE16
|unk_08053A20|
	CODE32
|arm_08053A20|
	STMDB    sp!, {r4, r5, r6, lr}
	EOR      r1, r1, r3
	EOR      r0, r0, r2
	EOR      r3, r3, r1
	EOR      r2, r2, r0
	EOR      r1, r1, r3
	EOR      r0, r0, r2
	B        |arm_08053A48|
	CODE16
	CODE16
	EXPORT |sub_08053A40|
