	CODE16
|unk_08046D1C|
	CODE32
	CMP      r2, #3
	BLS      |arm_08046E20|
	ANDS     ip, r0, #3
	BEQ      |arm_08046D50|
	LDRB     r3, [r1], #1
	CMP      ip, #2
	ADD      r2, r2, ip
|arm_08046D38|
	DCD     0x94D1C001
	STRB     r3, [r0], #1
|arm_08046D40|
	DCD     0x34D13001
	SUB      r2, r2, #4
|arm_08046D48|
	DCD     0x94C0C001
|arm_08046D4C|
	DCD     0x34C03001
|arm_08046D50|
	ANDS     r3, r1, #3
	BEQ      |arm_08046DD4|
	SUBS     r2, r2, #4
	BLO      |arm_08046E20|
	LDR      ip, [r1, -r3]!
	CMP      r3, #2
	BEQ      |arm_08046D90|
	BHI      |arm_08046DB0|
|arm_08046D70|
	MOV      r3, ip, LSR #8
	LDR      ip, [r1, #4]!
	SUBS     r2, r2, #4
	ORR      r3, r3, ip, lsl #24
	STR      r3, [r0], #4
	BHS      |arm_08046D70|
	ADD      r1, r1, #1
	B        |arm_08046E20|
|arm_08046D90|
	MOV      r3, ip, LSR #0x10
	LDR      ip, [r1, #4]!
	SUBS     r2, r2, #4
	ORR      r3, r3, ip, lsl #16
	STR      r3, [r0], #4
	BHS      |arm_08046D90|
	ADD      r1, r1, #2
	B        |arm_08046E20|
|arm_08046DB0|
	MOV      r3, ip, LSR #0x18
	LDR      ip, [r1, #4]!
	SUBS     r2, r2, #4
	ORR      r3, r3, ip, lsl #8
	STR      r3, [r0], #4
	BHS      |arm_08046DB0|
	ADD      r1, r1, #3
	B        |arm_08046E20|
	CODE16
	CODE16
	EXPORT |sub_08046DD0|
