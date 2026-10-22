	CODE16
|sub_080701EC|
	LSL      r6, r1, #3
	ADD      r3, pc, #0x0
|loc_080701F0|
	LSL      r0, r0, #0
	LSL      r0, r7, #1
	LDR      r0, [r0, r4]
	LSL      r0, r0, #0
	B        |loc_0806FFFA|
|sub_080701FA|
; cited by 0x0807000C (a pc-relative load targets 0x08070210)
	INCLUDE rawlabeled_701fa.s
