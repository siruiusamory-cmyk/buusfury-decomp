	CODE16
|unk_08053698|
	CODE32
|arm_08053698|
	STMDB    sp!, {r4, lr}
	LDR      ip, [pc, #0x29c]
|arm_080536A0|
	DCD     0xE1DC4081
|arm_080536A4|
	DCD     0x11DC4083
	BEQ      |arm_080536C0|
	TEQ      r1, r3
	EOR      r1, r1, #128, 8
	BMI      |arm_080534C8|
	EOR      r3, r3, #128, 8
	B        |arm_08053700|
|arm_080536C0|
	EOR      r1, r1, r3
	EOR      r0, r0, r2
	EOR      r3, r3, r1
	EOR      r2, r2, r0
	EOR      r1, r1, r3
	EOR      r0, r0, r2
	B        |arm_080538D0|
	CODE16
	CODE16
	EXPORT |sub_080536DC|
