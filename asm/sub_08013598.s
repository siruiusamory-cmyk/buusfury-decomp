	CODE16
|sub_08013598|
	MOV      r2, #0x56
	LDRB     r2, [r2, r0]
	MUL      r2, r1
	ASR      r1, r2, #4
	B        |sub_08013504|
