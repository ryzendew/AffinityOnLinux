using Mono.Cecil;
using Mono.Cecil.Cil;

internal class Program
{
    private const int StartInstructionOffset = 0; // IL Offset of the first instruction to remove (start of the 'if' condition)
    private const int EndInstructionOffset = 63;   // IL Offset of the last instruction to remove (end of the 'base.OnMainWindowLoaded' call)
    private const string AssemblyFileName = "Serif.Affinity.dll";
    private const string TargetClass = "Serif.Affinity.Application";
    private const string TargetMethod = "OnMainWindowLoaded";

    public static void Main(string[] args)
    {
        if (args.Length != 1)
        {
            Console.WriteLine("Error: Please provide the full path to the Affinity DLL to patch.");
            Console.WriteLine($"Usage: dotnet AffinityPatcher.dll \"/path/to/{AssemblyFileName}\"");
            return;
        }

        string assemblyPath = args[0];
        string backupPath = assemblyPath + ".bak";

        if (!File.Exists(assemblyPath))
        {
            Console.WriteLine($"Error: Assembly not found at {assemblyPath}");
            return;
        }

        var fileInfo = new FileInfo(assemblyPath);
        if (fileInfo.Length == 0)
        {
            Console.WriteLine("Assembly file is empty. Attempting to restore from backup...");
            if (File.Exists(backupPath))
            {
                File.Copy(backupPath, assemblyPath, overwrite: true);
                Console.WriteLine("Restored from backup.");
            }
            else
            {
                Console.WriteLine("No backup available. Cannot proceed.");
                return;
            }
        }

        try
        {
            if (!File.Exists(backupPath))
            {
                File.Copy(assemblyPath, backupPath);
                Console.WriteLine($"Created backup at: {backupPath}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error creating backup: {ex.Message}");
            return;
        }

        AssemblyDefinition? assembly = null;
        try
        {
            var readerParameters = new ReaderParameters { ReadSymbols = false };

            assembly = AssemblyDefinition.ReadAssembly(assemblyPath, readerParameters);

            var appType = assembly.MainModule.Types.FirstOrDefault(t => t.FullName.Contains(TargetClass));
            var targetMethod = appType?.Methods.FirstOrDefault(m => m.Name == TargetMethod);

            if (targetMethod == null)
            {
                Console.WriteLine($"Error: Could not find method {TargetClass}.{TargetMethod}");
                return;
            }

            ApplyNopPatch(targetMethod);

            string tempPath = assemblyPath + ".tmp";
            try
            {
                assembly.Write(tempPath);
                File.Move(tempPath, assemblyPath, overwrite: true);
                Console.WriteLine($"\nSUCCESS: Patch applied to {TargetMethod} in {AssemblyFileName}.");
                Console.WriteLine("Affinity should now register window events on startup.");
            }
            catch (Exception writeEx)
            {
                Console.WriteLine($"Error writing assembly: {writeEx.Message}");
                if (File.Exists(tempPath))
                {
                    File.Delete(tempPath);
                }
                throw;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\nCRITICAL ERROR during patching: {ex.Message}");
            Console.WriteLine("The original DLL was restored from backup (if created). Please correct the CIL offsets.");
        }
        finally
        {
            assembly?.Dispose();
        }
    }
    
    private static void ApplyNopPatch(MethodDefinition method)
    {
        var instructions = method.Body.Instructions;
        
        var startInstruction = instructions.FirstOrDefault(i => i.Offset == StartInstructionOffset);
        var endInstruction = instructions.FirstOrDefault(i => i.Offset == EndInstructionOffset);
        
        if (startInstruction == null || endInstruction == null)
        {
            Console.WriteLine($"\nERROR: Could not find CIL instructions for offsets 0x{StartInstructionOffset:X4} or 0x{EndInstructionOffset:X4}.");
            Console.WriteLine("Please verify the CIL offsets in dnSpy and update the constants.");
            throw new InvalidOperationException("Invalid CIL offsets detected.");
        }

        int startIndex = instructions.IndexOf(startInstruction);
        int endIndex = instructions.IndexOf(endInstruction);

        if (endIndex < startIndex)
        {
            Console.WriteLine("\nERROR: End offset is before the start offset. Check your constants.");
            throw new InvalidOperationException("Invalid CIL instruction index range.");
        }
        
        for (int i = startIndex; i <= endIndex; i++)
        {
            Instruction currentInstruction = instructions[i];
            
            currentInstruction.OpCode = OpCodes.Nop;
            currentInstruction.Operand = null;
        }
    }
}