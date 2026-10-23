	CODE16
|loc_0803F26A|
	LDR      r1, [pc, #0x15c]
	MOV      r0, #0
	STRH     r0, [r1, #2]
	SUB      r1, #0x40
	STRH     r0, [r1, #6]
	STRH     r0, [r1, #0x12]
	BX       lr
|loc_0803F278|
	DCW      0x484f
