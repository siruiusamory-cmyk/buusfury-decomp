	CODE16
|unk_08053120|
; cited by 0x08053120 (a pc-relative load targets 0x08053138)
	CODE32
	LDR      r3, [pc, #0x10]
	UMULL    r1, r2, r3, r0
	MVN      r3, #9
	MOV      r1, r2, LSR #3
	MLA      r0, r3, r1, r0
	BX       lr
|arm_08053138|
	DCD     0xCCCCCCCD
	CODE16
	CODE16
	EXPORT |sub_0805313C|
