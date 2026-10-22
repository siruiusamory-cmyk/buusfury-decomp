	CODE16
|__default_signal_handler|
	PUSH     {r3, r4, r5, lr}
	SUB      r2, r0, #1
	CMP      r2, #0xd
	ADD      r4, pc, #0x90
	BCS      |sub_080480AC|
	MOV      r2, #0x17
	LDR      r3, [pc, #0x8c]
	MUL      r2, r0
	ADD      r3, pc
	ADD      r5, r2, r3
	SUB      r5, #0x17
	CMP      r0, #2
	BNE      |loc_08048098|
	LSL      r0, r1, #5
	BPL      |sub_08048076|
	ADD      r4, pc, #0x80
	B        |loc_080480AE|
