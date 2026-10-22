	CODE16
|unk_08054F14|
	CODE32
|arm_08054F14|
	STMDB    sp!, {ip, lr}
	STMDB    sp!, {ip, lr}
|arm_08054F1C|
	DCD     0xEBFFD0B0
	LDMIA    sp!, {ip, lr}
	LDMIA    sp!, {ip, lr}
	AND      r3, ip, #0xf
	TEQ      r3, #9
	BXNE     lr
	B        |arm_08054F3C|
	CODE16
	CODE16
	EXPORT |sub_08054F38|
