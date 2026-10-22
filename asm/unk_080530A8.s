	CODE16
|unk_080530A8|
; cited by 0x080530A8 (a pc-relative load targets 0x080530C4)
	CODE32
	LDR      r3, [pc, #0x14]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	MVN      r3, #2
	RSB      r1, r2, r1
	MLA      r0, r3, r1, r0
	BX       lr
|arm_080530C4|
	DCD     0x55555556
	CODE16
	CODE16
	EXPORT |sub_080530C8|
