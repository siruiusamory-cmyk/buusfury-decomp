	CODE16
|unk_08053140|
; cited by 0x08053140 (a pc-relative load targets 0x08053158)
	CODE32
	LDR      r3, [pc, #0x10]
	UMULL    r1, r2, r3, r0
	MVN      r3, #0x3b
	MOV      r1, r2, LSR #5
	MLA      r0, r3, r1, r0
	BX       lr
|arm_08053158|
	DCD     0x88888889
	CODE16
	CODE16
	EXPORT |sub_0805315C|
