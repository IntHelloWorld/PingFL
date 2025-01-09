package com.qyh.agent;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.security.ProtectionDomain;
import java.util.HashSet;
import javassist.*;
import javassist.bytecode.CodeAttribute;
import java.io.*;

public class ClassTransformer implements ClassFileTransformer {
    private String runLogFile;
    private String srcClassPath;
    private String testClassPath;
    private final static HashSet<String> runedMethodsInfo = new HashSet<String>();

    public ClassTransformer(String outputDir, String srcClassPath, String testClassPath) {
        this.runLogFile = outputDir + File.separator + "run.log";
        this.srcClassPath = srcClassPath;
        this.testClassPath = testClassPath;

        Runtime.getRuntime().addShutdownHook(new Thread() {
            public void run() {
                writeRunLog(runLogFile);
            }
        });
    }

    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
        String classPath = protectionDomain.getCodeSource().getLocation().getPath();
        if (!classPath.contains(srcClassPath) && !classPath.contains(testClassPath)) {
            return null;
        }

        try {
            className = className.replace("/", ".");
            ClassPool pool = ClassPool.getDefault();
            CtClass ctClass = pool.get(className);
            
            for (CtMethod cm : ctClass.getDeclaredMethods()) {
                transformMethod(cm);
            }
            for (CtConstructor cc : ctClass.getConstructors()) {
                transformConstructor(cc);
            }
            return ctClass.toBytecode();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    private void transformConstructor(CtConstructor constructor)
            throws CannotCompileException, NotFoundException {
        CodeAttribute codeAttribute = constructor.getMethodInfo().getCodeAttribute();
        if (codeAttribute == null) return;

        CtClass declaringClass = constructor.getDeclaringClass();
        int startLine = constructor.getMethodInfo().getLineNumber(0);
        int endLine = constructor.getMethodInfo().getLineNumber(codeAttribute.getCodeLength());
        String lineRange = "(" + startLine + "-" + endLine + ")";

        String pkgName = declaringClass.getPackageName();
        String className = declaringClass.getSimpleName();
        String content = pkgName + "@" + className + ":" + constructor.getName() + lineRange;
        
        constructor.insertBefore(
            "com.qyh.agent.ClassTransformer.point(\"" + content + "\");"
        );
    }

    private void transformMethod(CtMethod method)
            throws CannotCompileException, NotFoundException {
        CodeAttribute codeAttribute = method.getMethodInfo().getCodeAttribute();
        if (codeAttribute == null) return;

        int startLine = method.getMethodInfo().getLineNumber(0);
        int endLine = method.getMethodInfo().getLineNumber(codeAttribute.getCodeLength());
        String lineRange = "(" + startLine + "-" + endLine + ")";

        CtClass declaringClass = method.getDeclaringClass();
        String pkgName = declaringClass.getPackageName();
        String className = declaringClass.getSimpleName();
        String content = pkgName + "@" + className + ":" + method.getName() + lineRange;
        
        method.insertBefore(
            "com.qyh.agent.ClassTransformer.point(\"" + content + "\");"
        );
    }

    public static void point(final String methodInfo) {
        runedMethodsInfo.add(methodInfo);
    }

    public static void writeRunLog(String runLogFile) {
        try {
            FileWriter fw = new FileWriter(runLogFile);
            for (String methodInfo : runedMethodsInfo) {
                fw.write(methodInfo + "\n");
            }
            fw.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
