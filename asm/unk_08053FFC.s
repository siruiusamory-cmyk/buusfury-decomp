	CODE16
|unk_08053FFC|
	CODE32
	ANDS     r3, r0, #128, 8
	RSBNE    r1, r0, #0
	MOVEQ    r1, r0
	ORR      r3, r3, #64, 8
|arm_0805400C|
	MOVS     r0, r1, LSR #0x10
	ADDNE    r3, r3, #64, 14
|arm_08054014|
	DCD     0x01B01801
	BXEQ     lr
	TST      r1, #0xff000000
	ADDNE    r3, r3, #128, 16
	MOVEQ    r1, r1, LSL #8
	TST      r1, #240, 8
	ADDNE    r3, r3, #64, 16
	MOVEQ    r1, r1, LSL #4
	TST      r1, #192, 8
	ADDNE    r3, r3, #128, 18
|arm_0805403C|
	DCD     0x01B01101
	ADDMI    r3, r3, #64, 18
	MOVPL    r1, r1, LSL #1
	MOV      r0, r1, LSL #0x15
	ADD      r1, r3, r1, asr #11
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08054054|
