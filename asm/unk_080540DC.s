	CODE16
|unk_080540DC|
; cited by 0x08053FB6 (a pc-relative load targets 0x080540E0)
	CODE32
	ORRS     ip, r1, r3
	BMI      |arm_08054114|
	CMN      ip, #64, 18
	BMI      |arm_080540FC|
	CMP      r1, r3
	BXNE     lr
	CMPEQ    r0, r2
	BX       lr
|arm_080540FC|
	CMN      r1, #64, 18
	CMNPL    r3, #64, 18
	BMI      |arm_08054150|
	CMP      r1, r3
	CMPEQ    r0, r2
	BX       lr
|arm_08054114|
	CMN      ip, #64, 18
	BPL      |arm_08054134|
	ORRS     ip, r0, r1, lsl #1
	ORREQS   ip, r2, r3, lsl #1
	CMPNE    r3, r1
	BXNE     lr
	CMPEQ    r2, r0
	BX       lr
|arm_08054134|
	MOV      ip, #128, 18
	CMN      ip, r1, lsl #1
	CMNLO    ip, r3, lsl #1
	BHS      |arm_08054150|
	CMP      r3, r1
	CMPEQ    r2, r0
	BX       lr
|arm_08054150|
	LDR      ip, [pc]
	B        |arm_080539B4|
	CODE16
	CODE16
	EXPORT |sub_08054158|
