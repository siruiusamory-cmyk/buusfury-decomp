	CODE16
|unk_08047FC4|
	CODE32
	STMDB    sp!, {r4, lr}
	BL       |arm_08047FB4|
	LDMIA    sp!, {r4, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08047FD4|
