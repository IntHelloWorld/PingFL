package com.qyh.agent;

import java.lang.instrument.Instrumentation;
import java.io.File;

public class ClassAgent {

    public static void premain(String argsString, Instrumentation inst) {
        String outputDir = null;
        String srcClassPath = null;
        String testClassPath = null;
        String[] args = argsString.split(",");
        for (String arg : args) {
            String[] kv = arg.split("=");
            String key = kv[0];
            String value = kv[1];
            switch (key) {
                case "outputDir":
                    outputDir = value;
                    break;
                case "srcClassPath":
                    srcClassPath = value;
                    break;
                case "testClassPath":
                    testClassPath = value;
                    break;
                default:
                    System.out.println("unknown arg: " + key);
                    return;
            }
        }
        
        if (outputDir == null || srcClassPath == null || testClassPath == null) {
            System.err.println("outputDir, srcClassPath or testClassPath is null");
            return;
        }

        ClassTransformer transformer = new ClassTransformer(outputDir, srcClassPath, testClassPath);
        inst.addTransformer(transformer);
    }
}