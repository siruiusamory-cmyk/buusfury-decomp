	CODE16
|unk_08046E44|
	CODE32
	AND      r3, r1, #0xff
	MOV      r1, r2
	ORR      r2, r3, r3, lsl #8
	ORR      r2, r2, r2, lsl #16
	B        |arm_08047A48|
	CODE16
	CODE16
	EXPORT |sub_08046E58|
