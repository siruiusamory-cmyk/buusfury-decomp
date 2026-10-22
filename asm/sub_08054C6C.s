	CODE16
|sub_08054C6C|
|unk_08054C6C|
	CODE32
|arm_08054C6C|
	MOV      r0, r0, LSL #8
	MOV      r1, r1, LSL #8
	TST      r2, #0xff0000
	BNE      |arm_08054CC0|
	CMP      r0, #64, 22
	SUBLO    r2, r2, #64, 18
	MOVLO    r0, r0, LSL #0x10
	TST      r0, #0xff000000
	SUBEQ    r2, r2, #128, 20
	MOVEQ    r0, r0, LSL #8
	TST      r0, #240, 8
	SUBEQ    r2, r2, #64, 20
	MOVEQ    r0, r0, LSL #4
	TST      r0, #192, 8
	SUBEQ    r2, r2, #128, 22
|arm_08054CA8|
	DCD     0x01B00100
	MOVPL    r0, r0, LSL #1
	ADDMI    r2, r2, #64, 22
	TST      r3, #0xff0000
	ORRNE    r1, r1, #128, 8
	MOVNE    pc, ip
|arm_08054CC0|
	ORR      r0, r0, #128, 8
	CMP      r1, #64, 22
	SUBLO    r3, r3, #64, 18
	MOVLO    r1, r1, LSL #0x10
	TST      r1, #0xff000000
	SUBEQ    r3, r3, #128, 20
	MOVEQ    r1, r1, LSL #8
	TST      r1, #240, 8
	SUBEQ    r3, r3, #64, 20
	MOVEQ    r1, r1, LSL #4
	TST      r1, #192, 8
	CODE16
