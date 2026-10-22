	CODE16
|unk_08047A2C|
	CODE32
|arm_08047A2C|
	STMDB    sp!, {r4, lr}
	BL       |arm_08047FB4|
	ADD      r0, r0, #4
	LDMIA    sp!, {r4, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08047A40|
