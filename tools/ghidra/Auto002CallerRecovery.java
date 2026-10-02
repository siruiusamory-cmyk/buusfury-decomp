/* ###
 * IP: Webfoot SDK
 *
 * AUTO-002: seed ROM-010's candidate query-caller entries plus the two
 * remaining established AABB query entries, verify callsite containment,
 * and emit a read-back report under build/ghidra/reports/.
 *
 * @category LOG1
 */

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SourceType;

public class Auto002CallerRecovery extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    private static final long[] ESTABLISHED_QUERY_ENTRIES = {
        0x080127AEL,
        0x08012846L,
    };

    private static final long[][] CALLER_SEEDS = {
        {0x08006E3CL, 0x08006E4EL},
        {0x08012A24L, 0x08012AECL},
        {0x08021CC0L, 0x08021DFEL},
        {0x08021CC0L, 0x08021E06L},
        {0x080220D8L, 0x08022142L},
    };

    private static final int DISASSEMBLY_PREVIEW_LIMIT = 32;

    private PrintWriter out;

    @Override
    public void run() throws Exception {
        requireExpectedProgram();

        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected output report path");
        }
        File report = requireIgnoredReportPath(args[0]);
        File parent = report.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
            throw new IllegalStateException("cannot create report directory: " + parent);
        }

        Register tMode = currentProgram.getProgramContext().getRegister("TMode");
        if (tMode == null) {
            throw new IllegalStateException("ARM TMode context register not found");
        }

        Map<Long, String> seedNames = new LinkedHashMap<>();
        seedNames.put(0x080127AEL, "aabb_query_080127AE");
        seedNames.put(0x08012846L, "aabb_query_08012846");
        seedNames.put(0x08006E3CL, "candidate_caller_08006E3C");
        seedNames.put(0x08012A24L, "candidate_caller_08012A24");
        seedNames.put(0x08021CC0L, "candidate_caller_08021CC0");
        seedNames.put(0x080220D8L, "candidate_caller_080220D8");

        Map<Long, String> statuses = new LinkedHashMap<>();
        int transaction = currentProgram.startTransaction("AUTO-002 caller seeding");
        boolean commit = false;
        try {
            for (Map.Entry<Long, String> seed : seedNames.entrySet()) {
                statuses.put(seed.getKey(),
                    ensureThumbFunction(seed.getValue(), seed.getKey(), tMode));
            }
            commit = statuses.values().stream().noneMatch(s -> s.startsWith("FAILED"));
        } finally {
            currentProgram.endTransaction(transaction, commit);
        }
        if (!commit) {
            throw new IllegalStateException("seeding failed; transaction rolled back: "
                + statuses);
        }

        try (PrintWriter writer = new PrintWriter(new OutputStreamWriter(
                new FileOutputStream(report), StandardCharsets.UTF_8))) {
            out = writer;
            out.println("AUTO2_REPORT");
            out.println("language=" + currentProgram.getLanguageID());
            out.println("executable_md5=" + currentProgram.getExecutableMD5());
            out.println("executable_sha256=" + currentProgram.getExecutableSHA256());
            out.println();
            for (Map.Entry<Long, String> seed : seedNames.entrySet()) {
                writeSeed(seed.getKey(), seed.getValue(), statuses.get(seed.getKey()));
            }
            out.println("CONTAINMENT_CHECKS");
            for (long[] pair : CALLER_SEEDS) {
                Function caller = currentProgram.getFunctionManager()
                    .getFunctionAt(addr(pair[0]));
                boolean contains = caller != null
                    && caller.getBody().contains(addr(pair[1]));
                out.printf("  caller=%08X callsite=%08X verdict=%s%n",
                    pair[0], pair[1], contains ? "CONTAINS" : "MISS");
            }
            out.println();
            for (long query : new long[] {0x080126D4L, 0x080127AEL, 0x08012846L}) {
                writeEntryReferences(query);
            }
            for (Long entry : seedNames.keySet()) {
                if (entry >= 0x08006E3CL) {
                    writeCallerDetail(entry);
                }
            }
        }
        println("AUTO-002 report written to " + report);
    }

    private String ensureThumbFunction(String desiredName, long raw, Register tMode)
            throws Exception {
        Address address = addr(raw);
        Instruction existing = currentProgram.getListing().getInstructionAt(address);
        BigInteger mode = currentProgram.getProgramContext()
            .getValue(tMode, address, false);
        if (existing != null && !BigInteger.ONE.equals(mode)) {
            return "FAILED_NOT_THUMB";
        }
        if (existing == null) {
            currentProgram.getProgramContext()
                .setValue(tMode, address, address, BigInteger.ONE);
            DisassembleCommand disassemble =
                new DisassembleCommand(address, null, true);
            if (!disassemble.applyTo(currentProgram, monitor)) {
                return "FAILED_DISASSEMBLE: " + disassemble.getStatusMsg();
            }
        }
        Function function = currentProgram.getFunctionManager().getFunctionAt(address);
        if (function == null) {
            Function containing =
                currentProgram.getFunctionManager().getFunctionContaining(address);
            if (containing != null) {
                return "MID_FUNCTION_OF " + containing.getEntryPoint();
            }
            CreateFunctionCmd create = new CreateFunctionCmd(address);
            if (!create.applyTo(currentProgram, monitor)) {
                return "FAILED_CREATE: " + create.getStatusMsg();
            }
            function = create.getFunction();
            if (function == null) {
                return "FAILED_CREATE_NO_FUNCTION";
            }
        }
        String currentName = function.getName();
        if (currentName.startsWith("FUN_") || currentName.startsWith("None")) {
            function.setName(desiredName, SourceType.USER_DEFINED);
        } else if (!currentName.equals(desiredName)) {
            return "EXISTING_NAME " + currentName;
        }
        return "OK";
    }

    private void writeSeed(long raw, String name, String status) {
        Function function = currentProgram.getFunctionManager().getFunctionAt(addr(raw));
        out.printf("SEED %08X name=%s status=%s%n", raw, name, status);
        if (function != null) {
            out.println("  entry=" + function.getEntryPoint());
            out.println("  body=" + formatBody(function));
            Instruction first = currentProgram.getListing()
                .getInstructionAt(function.getEntryPoint());
            out.println("  prologue=" + (first == null ? "NONE" : first.toString()));
        }
        out.println();
    }

    private void writeEntryReferences(long raw) {
        Address address = addr(raw);
        out.println("ENTRY_REFERENCES " + address);
        ReferenceIterator references =
            currentProgram.getReferenceManager().getReferencesTo(address);
        boolean any = false;
        while (references.hasNext()) {
            any = true;
            Reference reference = references.next();
            Function from = currentProgram.getFunctionManager()
                .getFunctionContaining(reference.getFromAddress());
            out.printf("  from=%s type=%s source_function=%s%n",
                reference.getFromAddress(), reference.getReferenceType(),
                from == null ? "NONE" : from.getEntryPoint() + " " + from.getName());
        }
        if (!any) {
            out.println("  NONE");
        }
        out.println();
    }

    private void writeCallerDetail(long raw) throws Exception {
        Function function = currentProgram.getFunctionManager().getFunctionAt(addr(raw));
        if (function == null) {
            out.println("CALLER_DETAIL " + String.format("%08X", raw) + " NONE");
            out.println();
            return;
        }
        out.println("CALLER_DETAIL " + function.getEntryPoint()
            + " " + function.getName());
        out.println("body=" + formatBody(function));
        out.println("callers:");
        writeFunctionSet(function.getCallingFunctions(monitor));
        out.println("callees:");
        writeFunctionSet(function.getCalledFunctions(monitor));
        out.println("disassembly_preview:");
        InstructionIterator instructions = currentProgram.getListing()
            .getInstructions(function.getBody(), true);
        int count = 0;
        while (instructions.hasNext() && count < DISASSEMBLY_PREVIEW_LIMIT) {
            Instruction instruction = instructions.next();
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            count++;
        }
        out.println("decompilation:");
        DecompInterface decompiler = new DecompInterface();
        try {
            decompiler.toggleCCode(true);
            if (!decompiler.openProgram(currentProgram)) {
                out.println("  OPEN_FAILED: " + decompiler.getLastMessage());
                return;
            }
            DecompileResults results =
                decompiler.decompileFunction(function, 90, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                out.println("  FAILED: " + results.getErrorMessage());
                return;
            }
            for (String line : results.getDecompiledFunction().getC().split("\\R", -1)) {
                out.println("  " + line);
            }
        } finally {
            decompiler.dispose();
        }
        out.println();
    }

    private void writeFunctionSet(Set<Function> functions) {
        if (functions.isEmpty()) {
            out.println("  NONE");
            return;
        }
        List<Function> sorted = new ArrayList<>(functions);
        sorted.sort(Comparator.comparing(Function::getEntryPoint));
        for (Function function : sorted) {
            out.printf("  %s %s%n", function.getEntryPoint(), function.getName());
        }
    }

    private String formatBody(Function function) {
        StringBuilder text = new StringBuilder();
        AddressRangeIterator ranges = function.getBody().getAddressRanges();
        while (ranges.hasNext()) {
            var range = ranges.next();
            if (text.length() != 0) {
                text.append(",");
            }
            text.append(range.getMinAddress()).append("..")
                .append(range.getMaxAddress());
        }
        return text.toString();
    }

    private Address addr(long raw) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(raw);
    }

    private void requireExpectedProgram() {
        String md5 = currentProgram.getExecutableMD5();
        String sha256 = currentProgram.getExecutableSHA256();
        String language = currentProgram.getLanguageID().toString();
        if (!EXPECTED_MD5.equalsIgnoreCase(md5) ||
                !EXPECTED_SHA256.equalsIgnoreCase(sha256) ||
                !EXPECTED_LANGUAGE.equals(language)) {
            throw new IllegalStateException(
                "refusing non-canonical program: md5=" + md5 +
                " sha256=" + sha256 + " language=" + language);
        }
    }

    private File requireIgnoredReportPath(String requestedPath) throws Exception {
        File source = getSourceFile().getFile(false);
        if (source == null || source.getParentFile() == null ||
                source.getParentFile().getParentFile() == null ||
                source.getParentFile().getParentFile().getParentFile() == null) {
            throw new IllegalStateException("cannot resolve repository from script path");
        }
        File repository = source.getParentFile().getParentFile().getParentFile();
        File allowedRoot = new File(repository, "build/ghidra/reports")
            .getCanonicalFile();
        File report = new File(requestedPath).getCanonicalFile();
        Path allowed = allowedRoot.toPath();
        Path candidate = report.toPath();
        if (candidate.equals(allowed) || !candidate.startsWith(allowed)) {
            throw new IllegalArgumentException(
                "report path must be below ignored directory " + allowedRoot);
        }
        return report;
    }
}
