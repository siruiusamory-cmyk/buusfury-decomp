	CODE16
|unk_08046F34|
; cited by 0x08046CF2 (a pc-relative load targets 0x08046F74)
	CODE32
	MOV      r2, #0
	RSBS     ip, r0, r1, lsr #3
	BLO      |arm_08046FC4|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046F88|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff000000
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046FB8|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046F88|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff0000
	RSBS     ip, r0, r1, lsr #8
	MOVHS    r0, r0, LSL #8
	ORRHS    r2, r2, #0xff00
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046FB8|
	RSBS     ip, r0, #0
	BHS      |arm_08047A1C|
|arm_08046F84|
	MOVHS    r0, r0, LSR #8
|arm_08046F88|
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
|arm_08046FB8|
	RSBS     ip, r0, r1, lsr #3
	SUBHS    r1, r1, r0, lsl #3
	ADC      r2, r2, r2
|arm_08046FC4|
	RSBS     ip, r0, r1, lsr #2
	SUBHS    r1, r1, r0, lsl #2
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #1
	SUBHS    r1, r1, r0, lsl #1
	ADC      r2, r2, r2
	RSBS     ip, r0, r1
	SUBHS    r1, r1, r0
	ADCS     r2, r2, r2
	BHS      |arm_08046F84|
	MOV      r0, r2
	BX       lr
	CODE16
	CODE16
	EXPORT |__vecmap1c__FPvT1iPFPv_v|
	EXPORT |loc_08047004|
	EXPORT |loc_08047010|
	EXPORT |loc_08047028|
	EXPORT |loc_0804703A|
	EXPORT |sub_08047040|
	EXPORT |sub_080476A6|
	EXPORT |sub_080476A8|
