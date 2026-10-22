	CODE16
|unk_08054058|
; cited by 0x0805405E (a pc-relative load targets 0x08054060)
	CODE32
|arm_08054058|
	ORRS     ip, r1, r3
	BMI      |arm_08054090|
	CMN      ip, #64, 18
	BMI      |arm_08054078|
	CMP      r1, r3
	BXNE     lr
	CMPEQ    r0, r2
	BX       lr
|arm_08054078|
	CMN      r1, #64, 18
	CMNPL    r3, #64, 18
	BMI      |arm_080540CC|
	CMP      r1, r3
	CMPEQ    r0, r2
	BX       lr
|arm_08054090|
	CMN      ip, #64, 18
	BPL      |arm_080540B0|
	ORRS     ip, r0, r1, lsl #1
	ORREQS   ip, r2, r3, lsl #1
	CMPNE    r3, r1
	BXNE     lr
	CMPEQ    r2, r0
	BX       lr
|arm_080540B0|
	MOV      ip, #128, 18
	CMN      ip, r1, lsl #1
	CMNLO    ip, r3, lsl #1
	BHS      |arm_080540CC|
	CMP      r3, r1
	CMPEQ    r2, r0
	BX       lr
|arm_080540CC|
	LDR      ip, [pc]
	B        |arm_080539B4|
	CODE16
	CODE16
	EXPORT |sub_080540D4|
