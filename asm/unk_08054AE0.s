	CODE16
|unk_08054AE0|
	CODE32
	ANDS     r2, r0, #128, 8
	RSBNE    r0, r0, #0
	ORR      r2, r2, #64, 8
|arm_08054AEC|
	MOVS     r1, r0, LSR #0x10
	ADDNE    r2, r2, #128, 12
|arm_08054AF4|
	DCD     0x01B00800
	BXEQ     lr
	TST      r0, #0xff000000
	ADDNE    r2, r2, #64, 12
	MOVEQ    r0, r0, LSL #8
	TST      r0, #240, 8
	ADDNE    r2, r2, #128, 14
	MOVEQ    r0, r0, LSL #4
	TST      r0, #192, 8
	ADDNE    r2, r2, #64, 14
|arm_08054B1C|
	DCD     0x01B00100
	ADDMI    r2, r2, #128, 16
	MOVPL    r0, r0, LSL #1
	MOVS     r1, r0, LSL #0x19
	ADC      r0, r2, r0, asr #8
	MOVNES   ip, #4, 2
|arm_08054B34|
	DCD     0x23C00001
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08054B3C|
