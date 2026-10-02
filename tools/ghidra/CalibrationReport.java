/* ###
 * IP: Webfoot SDK
 *
 * Headless, read-only report for TOOL-001's established calibration targets.
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
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;

public class CalibrationReport extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    private static final long[] TARGETS = {
        0x080126D4L,
        0x08007674L,
        0x08007768L,
        0x080125E8L,
        0x080075ACL,
    };

    private static final long[] DATA_TARGETS = {
        0x0804A09CL,
        0x0804A0ACL,
        0x080076A8L,
        0x080076ACL,
    };

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

        try (PrintWriter writer = new PrintWriter(new OutputStreamWriter(
                new FileOutputStream(report), StandardCharsets.UTF_8))) {
            out = writer;
            writeProgramSummary();
            writeEntryCheck(0x08000000L);
            writeEntryCheck(0x080000C0L);
            for (long target : TARGETS) {
                writeTarget(target);
            }
            for (long target : DATA_TARGETS) {
                writeDataTarget(target);
            }
        }

        println("TOOL-001 calibration report written to " + report);
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

    private void writeEntryCheck(long rawAddress) {
        Address address = currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(rawAddress);
        out.println("ENTRY_CHECK " + address);
        writeContext(address);
        writeSymbols(address);
        Function function = currentProgram.getFunctionManager().getFunctionContaining(address);
        out.println("function=" + (function == null ? "NONE" :
            function.getEntryPoint() + " " + function.getName()));
        Instruction instruction = currentProgram.getListing().getInstructionAt(address);
        out.println("instruction=" + (instruction == null ? "NONE" : instruction.toString()));
        out.println();
    }

    private void writeProgramSummary() {
        out.println("PROGRAM");
        out.println("name=" + currentProgram.getName());
        out.println("language=" + currentProgram.getLanguageID());
        out.println("compiler_spec=" + currentProgram.getCompilerSpec().getCompilerSpecID());
        out.println("image_base=" + currentProgram.getImageBase());
        out.println("executable_md5=" + currentProgram.getExecutableMD5());
        out.println("executable_sha256=" + currentProgram.getExecutableSHA256());
        out.println("memory_blocks:");
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            out.printf("  %s %s..%s read=%s write=%s execute=%s initialized=%s%n",
                block.getName(), block.getStart(), block.getEnd(), block.isRead(),
                block.isWrite(), block.isExecute(), block.isInitialized());
        }
        out.println();
    }

    private void writeTarget(long rawAddress) {
        Address address = currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(rawAddress);
        Function function = currentProgram.getFunctionManager().getFunctionContaining(address);

        out.println("TARGET " + address);
        writeContext(address);
        writeSymbols(address);

        if (function == null) {
            out.println("function=NOT_RECOVERED");
            writeLocalDisassembly(address);
            out.println();
            return;
        }

        out.println("function_name=" + function.getName());
        out.println("function_entry=" + function.getEntryPoint());
        out.println("function_body=" + formatBody(function));
        out.println("function_thunk=" + function.isThunk());
        out.println("parameter_count=" + function.getParameterCount());
        out.println("callers:");
        writeFunctionSet(function.getCallingFunctions(monitor));
        out.println("callees:");
        writeFunctionSet(function.getCalledFunctions(monitor));
        out.println("entry_references:");
        writeEntryReferences(function.getEntryPoint());
        out.println("outgoing_references:");
        writeOutgoingReferences(function);
        out.println("disassembly:");
        writeDisassembly(function);
        out.println("decompilation:");
        writeDecompilation(function);
        out.println();
    }

    private void writeContext(Address address) {
        Register tMode = currentProgram.getProgramContext().getRegister("TMode");
        if (tMode == null) {
            out.println("tmode=REGISTER_NOT_FOUND");
            return;
        }
        BigInteger value = currentProgram.getProgramContext().getValue(tMode, address, false);
        out.println("tmode=" + (value == null ? "UNSET" : value.toString()));
    }

    private void writeSymbols(Address address) {
        out.println("symbols:");
        Symbol[] symbols = currentProgram.getSymbolTable().getSymbols(address);
        if (symbols.length == 0) {
            out.println("  NONE");
            return;
        }
        for (Symbol symbol : symbols) {
            out.printf("  %s source=%s primary=%s%n", symbol.getName(true),
                symbol.getSource(), symbol.isPrimary());
        }
    }

    private String formatBody(Function function) {
        StringBuilder text = new StringBuilder();
        AddressRangeIterator ranges = function.getBody().getAddressRanges();
        while (ranges.hasNext()) {
            AddressRange range = ranges.next();
            if (text.length() != 0) {
                text.append(",");
            }
            text.append(range.getMinAddress()).append("..").append(range.getMaxAddress());
        }
        return text.toString();
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

    private void writeEntryReferences(Address entry) {
        ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(entry);
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
    }

    private void writeOutgoingReferences(Function function) {
        InstructionIterator instructions = currentProgram.getListing()
            .getInstructions(function.getBody(), true);
        boolean any = false;
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            Reference[] references = instruction.getReferencesFrom();
            for (Reference reference : references) {
                any = true;
                out.printf("  from=%s to=%s type=%s%n",
                    reference.getFromAddress(), reference.getToAddress(),
                    reference.getReferenceType());
            }
        }
        if (!any) {
            out.println("  NONE");
        }
    }

    private void writeDataTarget(long rawAddress) throws Exception {
        Address address = currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(rawAddress);
        out.println("DATA_TARGET " + address);
        writeSymbols(address);
        out.println("words:");
        for (int i = 0; i < 4; i++) {
            Address wordAddress = address.add(i * 4L);
            int value = currentProgram.getMemory().getInt(wordAddress);
            out.printf("  %s=0x%08X%n", wordAddress, value);
        }
        out.println("references:");
        writeEntryReferences(address);
        out.println();
    }

    private void writeDisassembly(Function function) {
        InstructionIterator instructions = currentProgram.getListing()
            .getInstructions(function.getBody(), true);
        int count = 0;
        while (instructions.hasNext() && count < 512) {
            Instruction instruction = instructions.next();
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            count++;
        }
        if (instructions.hasNext()) {
            out.println("  TRUNCATED_AFTER_512_INSTRUCTIONS");
        }
    }

    private void writeLocalDisassembly(Address address) {
        out.println("local_disassembly:");
        Instruction instruction = currentProgram.getListing().getInstructionAt(address);
        if (instruction == null) {
            out.println("  NONE");
            return;
        }
        for (int i = 0; instruction != null && i < 32; i++) {
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            instruction = instruction.getNext();
        }
    }

    private void writeDecompilation(Function function) {
        DecompInterface decompiler = new DecompInterface();
        try {
            decompiler.toggleCCode(true);
            decompiler.toggleSyntaxTree(true);
            if (!decompiler.openProgram(currentProgram)) {
                out.println("  OPEN_FAILED: " + decompiler.getLastMessage());
                return;
            }
            DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                out.println("  FAILED: " + results.getErrorMessage());
                return;
            }
            String code = results.getDecompiledFunction().getC();
            for (String line : code.split("\\R", -1)) {
                out.println("  " + line);
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
