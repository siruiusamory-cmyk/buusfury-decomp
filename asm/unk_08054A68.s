	CODE16
|unk_08054A68|
; cited by 0x08054A76 (a pc-relative load targets 0x08054A78)
	CODE32
	MOVS     r2, r0, ASR #0x17
	MOV      r3, r0, LSL #8
	ORRNE    r3, r3, #128, 8
	BMI      |arm_08054A88|
	RSBS     r2, r2, #0x9e
	BLS      |arm_08054AA8|
	MOV      r0, r3, LSR r2
	BX       lr
|arm_08054A88|
	CMP      r0, #0xcf000000
	BHI      |arm_08054AA8|
	ANDS     r2, r2, #0xff
|arm_08054A94|
	DCD     0x03C33480
	MOV      r0, #0
	RSBS     r2, r2, #0x9e
	SUB      r0, r0, r3, lsr r2
	BX       lr
|arm_08054AA8|
	LDR      ip, [pc, #0x1c]
	MOV      r1, r0, LSL #1
	CMP      r1, #0xff000000
	ORRHI    ip, ip, #64, 22
	BHI      |arm_08054A4C|
	BNE      |arm_08054850|
	B        |arm_08054AC4|
|arm_08054AC4|
	LDR      ip, [pc]
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08054ACC|
	EXPORT |sub_08054AD4|
	EXPORT |sub_08054ADC|
