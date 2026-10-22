	CODE16
|unk_08046E5C|
	CODE32
	ANDS     r2, r0, #128, 8
	RSBMI    r0, r0, #0
	EORS     r3, r2, r1, asr #32
	RSBHS    r1, r1, #0
	RSBS     ip, r0, r1, lsr #3
	BLO      |arm_08046EF8|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046EBC|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff000000
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046EEC|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046EBC|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff0000
	RSBS     ip, r0, r1, lsr #8
	MOVHS    r0, r0, LSL #8
	ORRHS    r2, r2, #0xff00
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046EEC|
	RSBS     ip, r0, #0
	BHS      |arm_08047A1C|
|arm_08046EB8|
	MOVHS    r0, r0, LSR #8
|arm_08046EBC|
	RSBS     ip, r0, r1, lsr #7
	SUBHS    r1, r1, r0, lsl #7
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #6
	SUBHS    r1, r1, r0, lsl #6
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #5
	SUBHS    r1, r1, r0, lsl #5
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #4
	SUBHS    r1, r1, r0, lsl #4
	ADC      r2, r2, r2
|arm_08046EEC|
	RSBS     ip, r0, r1, lsr #3
	SUBHS    r1, r1, r0, lsl #3
	ADC      r2, r2, r2
|arm_08046EF8|
	RSBS     ip, r0, r1, lsr #2
	SUBHS    r1, r1, r0, lsl #2
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #1
	SUBHS    r1, r1, r0, lsl #1
	ADC      r2, r2, r2
	RSBS     ip, r0, r1
	SUBHS    r1, r1, r0
	ADCS     r2, r2, r2
	BHS      |arm_08046EB8|
	EORS     r0, r2, r3, asr #31
	ADD      r0, r0, r3, lsr #31
	RSBHS    r1, r1, #0
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046F30|
