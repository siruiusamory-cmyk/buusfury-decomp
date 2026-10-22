	CODE16
|unk_080539B4|
	CODE32
|arm_080539B4|
	STMDB    sp!, {lr}
	MOV      lr, #128, 18
	CMN      lr, r1, lsl #1
	CMPEQ    r0, #0
	CMNLS    lr, r3, lsl #1
	CMPEQ    r2, #0
|arm_080539CC|
	DCD     0x8A00000E
	LDMIA    sp!, {lr}
|arm_080539D4|
	DCD     0xEAFFFFFF
	CODE16
	CODE16
	EXPORT |sub_080539D8|
	EXPORT |sub_080539DC|
	EXPORT |loc_08053A0C|
	EXPORT |sub_08053A1C|
