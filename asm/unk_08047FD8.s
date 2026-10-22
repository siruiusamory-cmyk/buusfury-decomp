	CODE16
|unk_08047FD8|
	CODE32
|arm_08047FD8|
	STMDB    sp!, {r4, lr}
|arm_08047FDC|
	DCD     0xEB00047D
	CMP      r0, #0
|arm_08047FE4|
	DCD     0x08BD4010
	BXEQ     lr
	LDMIA    sp!, {r4, lr}
	B        |arm_0804803C|
	CODE16
	CODE16
	EXPORT |__raise|
	EXPORT |loc_08048006|
	EXPORT |sub_0804801A|
	EXPORT |__16_sys_exit|
