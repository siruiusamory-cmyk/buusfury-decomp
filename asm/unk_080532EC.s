	CODE16
|unk_080532EC|
; cited by 0x08053326 (a pc-relative load targets 0x08053328)
	CODE32
	AND      r3, r1, #128, 8
	BIC      r1, r1, #128, 8
	EOR      r2, r1, r1, lsl #1
	TST      r2, #0x7f000000
	TSTEQ    r2, #224, 16
|arm_08053300|
	DCD     0x0A00002F
	MOV      ip, #192, 8
	MOVS     r2, r0, LSL #4
	BHI      |arm_08053328|
	BHS      |arm_0805331C|
	MOVEQ    ip, #0
|arm_08053318|
	DCD     0xEA000005
|arm_0805331C|
	AND      r2, r0, #128, 10
	ADDS     ip, ip, r2, lsl #2
|arm_08053324|
	DCD     0x4A000002
|arm_08053328|
	MOV      ip, #64, 8
	ADDS     r0, r0, #128, 10
	ADC      r1, r1, #0
	CODE16
	CODE16
	EXPORT |sub_08053334|
	EXPORT |sub_08053338|
	EXPORT |loc_080533C4|
	EXPORT |sub_0805349C|
