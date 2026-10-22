	INCLUDE asm/macros.inc
	INCLUDE asm/ram.inc

	CODE16
	AREA GBARam, CODE, READONLY
	

	thumb_func_start GBARam_Init__Fv
		LDR      r0,|GBARam_LocalVars|
		LDR      r1,|GBARam_LocalVars| + 4
		LDR      r2,|GBARam_LocalVars| + 8
		STR      r0,[r1,#0]
		MOV      r1,#0
		STRH     r1,[r0,#0]
		STRH     r2,[r0,#2]
		STRH     r1,[r0,#4]
		STRB     r1,[r0,#6]
		STRH     r1,[r0,#8]
		STRH     r1,[r0,#0xa]
		BX       lr
	thumb_func_end GBARam_Init__Fv

	thumb_func_start GBARam_MarkAsUsed__FP19struct_MallocHeader
        MOV      r1,#1
        STRB     r1,[r0,#6]
        LDRH     r2,[r0,#0xa]
        LSL      r3,r1,#25
        LDRH     r1,[r0,#8]
        CMP      r2,#0
        BEQ      |L1.46|
        LSL      r2,r2,#2
        ADD      r2,r2,r3
        STRH     r1,[r2,#8]
        B        |L1.64|
|L1.46|
        LDR      r2,|GBARam_LocalVars| + 4
        CMP      r1,#0
        BEQ      |L1.60|
        LSL      r1,r1,#2
        ADD      r1,r1,r3
        STR      r1,[r2,#0]
        B        |L1.64|
|L1.60|
        MOV      r1,#0
        STR      r1,[r2,#0]
|L1.64|
        LDRH     r1,[r0,#8]
        CMP      r1,#0
        BEQ      |L1.78|
        LDRH     r0,[r0,#0xa]
        LSL      r1,r1,#2
        ADD      r1,r1,r3
        STRH     r0,[r1,#0xa]
|L1.78|
        BX       lr
	thumb_func_end GBARam_MarkAsUsed__FP19struct_MallocHeader

	thumb_func_start GBARam_AddToFreeList__FP19struct_MallocHeader
        LDR      r3, |GBARam_LocalVars| + 4
        PUSH	 {r4,r5}
        LDR		 r1,[r3,#0]
        MOV		 r4,#0
        CMP		 r1,#0
        BEQ		 |GBARam_AddToFreeList_NULLBRANCH|
        MOV		 r5,#0x7f
        LSL		 r5,r5,#0x19
        ADD		 r2,r1,r5
        ASR		 r2,r2,#2
        STRH	 r2,[r0,#8]
        ADD		 r2,r0,r5
        ASR		 r2,r2,#2
        STRH	 r2,[r1,#0xa]
        B		 |GBARam_AddToFreeList_END|
|GBARam_AddToFreeList_NULLBRANCH|
        STRH	 r4,[r0,#0x8]
|GBARam_AddToFreeList_END|
        STRH	 r4,[r0,#0xa]
        STR		 r0,[r3,#0]
        POP		 {r4,r5}
        BX		 lr
	thumb_func_end GBARam_AddToFreeList__FP19struct_MallocHeader

	thumb_func_start GBARam_MergeWithNext__FP19struct_MallocHeader
        LDRH	 r2,[r0,#0x2]
        LDRH	 r3,[r1,#0x2]
        ADD		 r2,r2,r3
        ADD		 r2,#0x2
        STRH	 r2,[r0,#0x2]
        LDRH	 r2,[r1,#0x0]
        STRH	 r2,[r0,#0x0]
        LDRH	 r0,[r1,#0x0]
        CMP		 r0,#0x0
        BEQ		 |GBARam_MergeWithNext_END|
        MOV		 r2,#0x1
        LDRH	 r1,[r1,#0x4]
        LSL		 r2,r2,#0x19
        LSL		 r0,r0,#0x2
        ADD		 r0,r0,r2
        STRH	 r1,[r0,#0x4]
|GBARam_MergeWithNext_END|
        BX		 lr
	thumb_func_end GBARam_MergeWithNext__FP19struct_MallocHeader
	thumb_func_start GBARam_MergeWithNextFree__FP19struct_MallocHeader
        PUSH	 {r4,r5}
        LDRH	 r3,[r0,#0x2]
        LDRH	 r4,[r1,#0x2]
        LDRH	 r2,[r1,#0x4]
        ADD		 r3,r3,r4
        ADD		 r3,#0x2
        STRH	 r3,[r0,#0x2]
        LDRH	 r3,[r1,#0x0]
        MOV		 r4,#0x1
        LSL		 r4,r4,#0x19
        STRH	 r3,[r0,#0x0]
        LDRH	 r3,[r1,#0x0]
        CMP		 r3,#0x0
        BEQ		 |GBARam_MergeWithNextFree_HAS_NEXT|
        LDRH	 r5,[r1,#0x4]
        LSL		 r3,r3,#0x2
        ADD		 r3,r3,r4
        STRH	 r5,[r3,#0x4]
|GBARam_MergeWithNextFree_HAS_NEXT|
        LDRH	 r3,[r1,#0xa]
        STRH	 r3,[r0,#0xa]
        LDRH	 r3,[r1,#0xa]
        CMP		 r3,#0x0
        BEQ		 |GBARam_MergeWithNextFree_LAST_FREE_EXISTS|
        LSL		 r3,r3,#0x2
        ADD		 r3,r3,r4
        STRH	 r2,[r3,#0x8]
        B		 |GBARam_MergeWithNextFree_UPDATE_NEXT_FREE|
|GBARam_MergeWithNextFree_LAST_FREE_EXISTS|
        LDR      r3, |GBARam_LocalVars| + 4
        STR      r0, [r3,#0x0]
|GBARam_MergeWithNextFree_UPDATE_NEXT_FREE|
        LDRH	 r3,[r1,#0x8]
        STRH	 r3,[r0,#0x8]
        LDRH	 r0,[r1,#0x8]
        CMP		 r0,#0x0
        BEQ		 |GBARam_MergeWithNextFree_END|
        LSL		 r0,r0,#0x2
        ADD		 r0,r0,r4
        STRH	 r2,[r0,#0xa]
|GBARam_MergeWithNextFree_END|
        POP		 {r4,r5}
        BX		 lr
	thumb_func_end GBARam_MergeWithNextFree__FP19struct_MallocHeader
	thumb_func_start |GBARam_Malloc|
        PUSH     {r4,r5,r6,r7,lr}
        LDR      r1,|GBARam_LocalVars| + 4
        ADD      r0,#3
        LDR      r5,[r1]
        MOV      r1,#1
        ASR      r0,r0,#2
        MOV      r4,#0
        LDR      r3,|GBARam_LocalVars| + 12
        LSL      r1,r1,#0x19
|GBARam_Malloc_SCAN|
        LDRH     r2,[r5,#2]
        CMP      r2,r3
        BGE      |GBARam_Malloc_NEXT_FREE|
        CMP      r2,r0
        BNE      |GBARam_Malloc_CANDIDATE|
        ADD      r0,r5,#0
        BL       GBARam_MarkAsUsed__FP19struct_MallocHeader
        ADD      r0,r5,#0
        ADD      r0,#8
        POP      {r4,r5,r6,r7,pc}
|GBARam_Malloc_CANDIDATE|
        CMP      r2,r0
        BLE      |GBARam_Malloc_NEXT_FREE|
        ADD      r4,r5,#0
        ADD      r3,r2,#0
|GBARam_Malloc_NEXT_FREE|
        LDRH     r2,[r5,#8]
        CMP      r2,#0
        BEQ      |GBARam_Malloc_BEST_FOUND|
        LSL      r2,r2,#2
        ADD      r5,r2,r1
        B        |GBARam_Malloc_SCAN|
|GBARam_Malloc_BEST_FOUND|
        LDRH     r2,[r4,#2]
        SUB      r3,r2,r0
        SUB      r3,#2
        CMP      r3,#0
        BGT      |GBARam_Malloc_SPLIT|
        ADD      r0,r4,#0
        BL       GBARam_MarkAsUsed__FP19struct_MallocHeader
        ADD      r0,r4,#0
        ADD      r0,#8
        POP      {r4,r5,r6,r7,pc}
|GBARam_Malloc_SPLIT|
        LSL      r2,r3,#2
        ADD      r2,r2,r4
        ADD      r2,#8
        MOV      r7,#0x7f
        LDRH     r6,[r4]
        LSL      r7,r7,#0x19
        ADD      r5,r2,r7
        ASR      r5,r5,#2
        CMP      r6,#0
        STRH     r6,[r2]
        BEQ      |GBARam_Malloc_NO_NEXT_NEXT|
        LSL      r6,r6,#2
        ADD      r1,r6,r1
        STRH     r5,[r1,#4]
|GBARam_Malloc_NO_NEXT_NEXT|
        STRH     r0,[r2,#2]
        ADD      r0,r4,r7
        ASR      r0,r0,#2
        STRH     r0,[r2,#4]
        MOV      r0,#1
        STRB     r0,[r2,#6]
        STRH     r5,[r4]
        ADD      r0,r2,#0
        ADD      r0,#8
        STRH     r3,[r4,#2]
        POP      {r4,r5,r6,r7,pc}
	thumb_func_end |GBARam_Malloc|
	thumb_func_start |GBARam_Free|
        PUSH     {r4,r5,r6,r7,lr}
        CMP      r0,#0
        BEQ      |GBARam_Free_END|
        ADD      r4,r0,#0
        SUB      r4,#8
        MOV      r1,#0
        STRB     r1,[r4,#6]
        LDRH     r0,[r4]
        MOV      r7,#1
        LSL      r7,r7,#0x19
        CMP      r0,#0
        BEQ      |GBARam_Free_NO_FREE_LIST|
        LSL      r0,r0,#2
        ADD      r6,r0,r7
        LDRH     r0,[r4,#4]
        CMP      r0,#0
        BEQ      |GBARam_Free_NEXT_USED|
        LSL      r0,r0,#2
        ADD      r5,r0,r7
        LDRB     r0,[r6,#6]
        CMP      r0,#0
        LDRB     r0,[r5,#6]
        BNE      |GBARam_Free_BOTH_FREE|
        CMP      r0,#0
        BNE      |GBARam_Free_NEXT_FREE|
        ADD      r0,r6,#0
        BL       GBARam_MarkAsUsed__FP19struct_MallocHeader
        LDRH     r0,[r4,#2]
        LDRH     r1,[r6,#2]
        ADD      r0,r0,r1
        LDRH     r1,[r5,#2]
        ADD      r0,r0,r1
        ADD      r0,#4
        STRH     r0,[r5,#2]
        LDRH     r0,[r6]
        STRH     r0,[r5]
        LDRH     r0,[r6]
        CMP      r0,#0
        BEQ      |GBARam_Free_END|
        LDRH     r1,[r4,#4]
        LSL      r0,r0,#2
        ADD      r0,r0,r7
        STRH     r1,[r0,#4]
|GBARam_Free_END|
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_NEXT_FREE|
        ADD      r1,r6,#0
        ADD      r0,r4,#0
        BL       GBARam_MergeWithNextFree__FP19struct_MallocHeader
|GBARam_Free_EXIT|
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_BOTH_FREE|
        CMP      r0,#0
        BNE      |GBARam_Free_NEXT_USED_FREE|
        LDRH     r0,[r5,#2]
        LDRH     r1,[r4,#2]
        ADD      r0,r0,r1
        ADD      r0,#2
        STRH     r0,[r5,#2]
        LDRH     r0,[r4]
        STRH     r0,[r5]
        LDRH     r0,[r4]
        CMP      r0,#0
        BEQ      |GBARam_Free_EXIT|
        LDRH     r1,[r4,#4]
        LSL      r0,r0,#2
        ADD      r0,r0,r7
        STRH     r1,[r0,#4]
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_NEXT_USED_FREE|
        ADD      r0,r4,#0
        BL       GBARam_AddToFreeList__FP19struct_MallocHeader
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_NEXT_USED|
        LDRB     r0,[r6,#6]
        CMP      r0,#0
        BNE      |GBARam_Free_PREV_USED|
        ADD      r1,r6,#0
        ADD      r0,r4,#0
        BL       GBARam_MergeWithNextFree__FP19struct_MallocHeader
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_PREV_USED|
        ADD      r0,r4,#0
        BL       GBARam_AddToFreeList__FP19struct_MallocHeader
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_NO_FREE_LIST|
        LDRH     r0,[r4,#4]
        CMP      r0,#0
        BEQ      |GBARam_Free_APPEND_LAST|
        LSL      r0,r0,#2
        ADD      r0,r0,r7
        LDRB     r2,[r0,#6]
        CMP      r2,#0
        BNE      |GBARam_Free_NEXT_USED_ADD|
        LDRH     r2,[r0,#2]
        LDRH     r3,[r4,#2]
        ADD      r2,r2,r3
        ADD      r2,#2
        STRH     r2,[r0,#2]
        STRH     r1,[r0]
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_NEXT_USED_ADD|
        ADD      r0,r4,#0
        BL       GBARam_AddToFreeList__FP19struct_MallocHeader
        POP      {r4,r5,r6,r7,pc}
|GBARam_Free_APPEND_LAST|
        LDR      r0,|GBARam_LocalVars| + 4
        STR      r4,[r0]
        STRH     r1,[r4,#8]
        STRH     r1,[r4,#0xa]
        POP      {r4,r5,r6,r7,pc}
	thumb_func_end |GBARam_Free|
	thumb_func_start |GBARam_Free_LARGEST|
        LDR      r1,|GBARam_LocalVars| + 4
        MOV      r0,#0
        MOV      r3,#1
        LDR      r1,[r1]
        LSL      r3,r3,#0x19
|GBARam_Free_LARGEST_LOOP|
        LDRH     r2,[r1,#2]
        LDRH     r1,[r1,#8]
        LSL      r2,r2,#2
        ADD      r0,r2,r0
        CMP      r1,#0
        BEQ      |GBARam_Free_LARGEST_RET|
        LSL      r1,r1,#2
        ADD      r1,r1,r3
        B        |GBARam_Free_LARGEST_LOOP|
|GBARam_Free_LARGEST_RET|
        BX       lr
	thumb_func_end |GBARam_Free_LARGEST|
|GBARam_LocalVars| DATA
        DCD      g_HeapStart
        DCD      g_FreeListTail
        DCD      HEAP_WORDS
		DCD      INT_MAX
	END