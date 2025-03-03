package com.qyh.agent;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Stack;

import org.jgrapht.Graph;
import org.jgrapht.graph.DefaultDirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;
import org.jgrapht.nio.gml.GmlExporter;
import org.jgrapht.nio.gml.GmlExporter.Parameter;

public class MethodStack {

    private static Stack<String> stack = new Stack<>();
    private static Graph<String, DefaultWeightedEdge> graph = new DefaultDirectedWeightedGraph<>(DefaultWeightedEdge.class);
    // static FileWriter fw;
    // static StringBuffer sb;
    static long threadid = -1L;

    static {
        Runtime.getRuntime().addShutdownHook(new Thread() {
            public void run() {
                // try {
                //     fw.close();
                // } catch (IOException e) {
                //     e.printStackTrace();
                // }
                GmlExporter<String, DefaultWeightedEdge> exporter = new GmlExporter<>();
                exporter.setParameter(Parameter.EXPORT_EDGE_WEIGHTS, true);
                exporter.setParameter(Parameter.EXPORT_VERTEX_LABELS, true);
                File file = new File("callgraph.graphml");
                try (FileWriter writer = new FileWriter(file)) {
                    exporter.exportGraph(graph, writer);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        // File log = new File("calltrace.txt");
        // try {
        //     fw = new FileWriter(log);
        // } catch (Exception e) {
        //     e.printStackTrace();
        // }
        // sb = new StringBuffer();
    }

    public static void push(String content) throws IOException {
        if (threadid == -1)
            threadid = Thread.currentThread().getId();
        
        if (Thread.currentThread().getId() != threadid)
            return;
        
        // add call level
        // sb.setLength(0);
        // sb.append("[").append(stack.size()).append("]#");

        // Add callsite information
        // StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        // if (stackTrace.length > 3) { // Index 0 is getStackTrace, 1 is push, 2 is the instrumented method
        //     StackTraceElement caller = stackTrace[3];
        //     sb.append(caller.getFileName().split("\\.")[0])
        //             .append(":")
        //             .append(caller.getLineNumber());
        // } else {
        //     sb.append("unknown");
        // }
        // sb.append("#");

        // add called method info
        // sb.append(content);

        // add node
        graph.addVertex(content);

        // add edge
        if (!stack.isEmpty()) {
            DefaultWeightedEdge edge = graph.addEdge(stack.peek(), content);
            if (edge == null) {  // edge already exists
                DefaultWeightedEdge e = graph.getEdge(stack.peek(), content);
                graph.setEdgeWeight(e, graph.getEdgeWeight(e) + 1.0);
            } else {
                graph.setEdgeWeight(edge, 1.0);
            }
        }

        // sb.append("\n");
        // fw.write(sb.toString());
        stack.push(content);
    }

    public static void pop() throws IOException {
        if (threadid == -1)
            threadid = Thread.currentThread().getId();

        if (Thread.currentThread().getId() != threadid)
            return;

        if (stack.isEmpty()) {
            return;
        }
        stack.pop();
    }
}