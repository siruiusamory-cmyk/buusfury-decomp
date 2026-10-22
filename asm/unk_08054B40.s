	CODE16
|unk_08054B40|
; cited by 0x08054766 (a pc-relative load targets 0x08054B64)
	CODE32
	MOV      ip, #0xff0000
	ANDS     r2, ip, r0, lsr #7
	ANDNES   r3, ip, r1, lsr #7
	TEQNE    r2, ip
	TEQNE    r3, ip
	BEQ      |arm_08054C04|
	TEQ      r0, r1
	ORRMI    r2, r2, #64, 30
	MOV      ip, #128, 8
	ORR      r0, ip, r0, lsl #8
	ORR      r1, ip, r1, lsl #8
	ADD      r2, r2, r3
	UMULL    ip, r3, r0, r1
	SUB      r2, r2, #128, 16
	CMP      ip, #0
	ORRNE    r3, r3, #1
	AND      ip, r2, #64, 30
	CMP      r3, #128, 8
	MOVLO    r3, r3, LSL #1
	ADC      r2, r2, r2, asr #16
	MOVS     r0, r3, LSR #8
	ADC      r0, r0, r2, lsl #23
	ADC      ip, sp, r0, lsl #1
	TSTHS    r3, #0x7f
	CMPNE    r2, #252, 16
	BXLO     lr
|arm_08054BA8|
	DCD     0x03C00001
	CMP      r2, #252, 16
	BXLO     lr
	BPL      |arm_08054BEC|
	MOV      r1, r0, LSL #1
	SUB      r1, r1, #64, 14
	CMP      r1, #192, 14
	BXLO     lr
	ADD      r0, r0, #96, 8
	TST      r3, #0x7f
|arm_08054BD0|
	DCD     0x11B0C0EC
	MVNEQS   ip, ip, ror #2
	MOVMI    r2, #208, 6
	MOVPL    r2, #240, 6
	TST      r3, #0xff
	MOVEQ    r2, #3
	B        |arm_08054D04|
|arm_08054BEC|
	ADD      ip, r0, #128, 16
	MOVS     ip, ip, LSL #1
	BXMI     lr
	SUB      r0, r0, #96, 8
	MOV      ip, #196, 6
	B        |arm_08054850|
|arm_08054C04|
	AND      r3, ip, r1, lsr #7
	TEQ      r0, r1
	ORRMI    r2, r2, #64, 30
	CMP      r2, ip
	CMPLO    r3, ip
	BHS      |arm_08054C34|
	MOVS     ip, r0, LSL #1
|arm_08054C20|
	DCD     0x11B0C081
	MOVEQ    r0, r2, LSL #0x17
	BXEQ     lr
	SUB      ip, pc, #0xc8
	B        |arm_08054C6C|
|arm_08054C34|
	MOV      ip, #64, 14
	CMN      ip, r0, lsl #1
	CMNLS    ip, r1, lsl #1
	MOV      ip, #0x4000003
	BHI      |arm_08054A24|
	B        |arm_08054C4C|
|arm_08054C4C|
	MOVS     ip, r0, LSL #1
|arm_08054C50|
	DCD     0x11B0C081
	ORRNE    r2, r2, #0xff
	MOVNE    r0, r2, LSL #0x17
	BXNE     lr
	MOV      ip, #0x4000003
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08054C68|
	EXPORT |sub_08054C6C|
	EXPORT |sub_08054CEC|
