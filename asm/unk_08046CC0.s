	CODE16
|unk_08046CC0|
	CODE32
	MOV      r2, #0
|arm_08046CC4|
	STMDB    sp!, {lr}
	MOV      r3, r2
	MOV      ip, r2
	MOV      lr, r2
	SUBS     r1, r1, #0x20
|arm_08046CD8|
	DCD     0x28A0500C
|arm_08046CDC|
	DCD     0x28A0500C
	SUBHSS   r1, r1, #0x20
	BHS      |arm_08046CD8|
	MOVS     r1, r1, LSL #0x1c
|arm_08046CEC|
	DCD     0x28A0500C
|arm_08046CF0|
	DCD     0x48A0000C
	LDMIA    sp!, {lr}
	MOVS     r1, r1, LSL #2
	STRHS    r2, [r0], #4
	BXEQ     lr
|arm_08046D04|
	DCD     0x44C02001
|arm_08046D08|
	DCD     0x44C02001
	TST      r1, #64, 8
|arm_08046D10|
	DCD     0x14C02001
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046D18|
