	CODE16
|unk_08046B3C|
	CODE32
|arm_08046B3C|
	STMDB    sp!, {r4, r5, r6, lr}
	MOV      lr, r0
	UMULL    r0, ip, r2, lr
	MLA      r1, r2, r1, ip
	MLA      r1, r3, lr, r1
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046B58|
	EXPORT |sub_08046B5C|
	EXPORT |sub_08046B64|
	EXPORT |sub_08046B68|
	EXPORT |sub_08046B70|
