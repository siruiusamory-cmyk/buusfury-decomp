/* ###
 * IP: Webfoot SDK
 *
 * AUTO-003: seed ROM-012 bounded-trace sites and report the executable tree
 * around the accepted spatial action chain.
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
import ghidra.program.model.symbol.SourceType;

public class Auto003ActionTree extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    private static final long[][] SEEDS = {
        {0x080077ECL, 0},
        {0x08009744L, 0},
        {0x080094B8L, 0},
    };

    private static final long[] REPORT_TARGETS = {
        0x080125E8L,
        0x080075ACL,
        0x080077ECL,
        0x08009744L,
        0x080094B8L,
    };

    private static final int DISASSEMBLY_LIMIT = 400;

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

        Map<Long, String> statuses = new LinkedHashMap<>();
        int transaction = currentProgram.startTransaction("AUTO-003 trace-site seeding");
        boolean commit = false;
        try {
            int index = 0;
            for (long[] seed : SEEDS) {
                String name = "candidate_trace_site_" + String.format("%08X", seed[0]);
                statuses.put(seed[0], ensureThumbFunction(name, seed[0], tMode));
                index++;
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
            out.println("AUTO3_REPORT");
            out.println("language=" + currentProgram.getLanguageID());
            out.println("executable_sha256=" + currentProgram.getExecutableSHA256());
            out.println();
            for (long target : REPORT_TARGETS) {
                writeTarget(target);
            }
        }
        println("AUTO-003 report written to " + report);
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

    private void writeTarget(long raw) throws Exception {
        Function function = currentProgram.getFunctionManager()
            .getFunctionContaining(addr(raw));
        out.println("TARGET " + String.format("%08X", raw));
        if (function == null) {
            out.println("function=NOT_RECOVERED");
            out.println();
            return;
        }
        out.println("function_name=" + function.getName());
        out.println("function_entry=" + function.getEntryPoint());
        out.println("function_body=" + formatBody(function));
        out.println("callers:");
        writeFunctionSet(function.getCallingFunctions(monitor));
        out.println("callees:");
        writeFunctionSet(function.getCalledFunctions(monitor));
        out.println("disassembly:");
        InstructionIterator instructions = currentProgram.getListing()
            .getInstructions(function.getBody(), true);
        int count = 0;
        while (instructions.hasNext() && count < DISASSEMBLY_LIMIT) {
            Instruction instruction = instructions.next();
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            count++;
        }
        if (instructions.hasNext()) {
            out.println("  TRUNCATED_AFTER_" + DISASSEMBLY_LIMIT);
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
                decompiler.decompileFunction(function, 120, monitor);
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
