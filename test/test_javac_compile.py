log = """
Running ant (compile.tests)................................................ FAIL
Executed command:  cd /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166 && /home/qyh/DATASET/defects4j-2.0.1/major/bin/ant -f /home/qyh/DATASET/defects4j-2.0.1/framework/projects/defects4j.build.xml -Dd4j.home=/home/qyh/DATASET/defects4j-2.0.1 -Dd4j.dir.projects=/home/qyh/DATASET/defects4j-2.0.1/framework/projects -Dbasedir=/home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166 -Dbuild.compiler=javac1.7  compile.tests 2>&1
Java HotSpot(TM) 64-Bit Server VM warning: ignoring option MaxPermSize=1G; support was removed in 8.0
Buildfile: /home/qyh/DATASET/defects4j-2.0.1/framework/projects/defects4j.build.xml

rhino:

properties:

init:
    [mkdir] Created dir: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib
    [mkdir] Created dir: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes
    [mkdir] Created dir: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/rhino1_7R5pre

compile:

compile-most:
    [javac] Compiling 217 source files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes
    [javac] warning: [options] bootstrap class path not set in conjunction with -source 1.5
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Object.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Arrays.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/String.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/OutputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/IOException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/Serializable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/ObjectInputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/ObjectOutputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/ClassNotFoundException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/RuntimeException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Exception.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Throwable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Class.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Annotation.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/AccessibleObject.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Constructor.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/InvocationTargetException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Member.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Method.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Modifier.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/HashMap.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/HashSet.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Map.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/beans/PropertyChangeEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/beans/PropertyChangeListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/CharArrayWriter.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/PrintWriter.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/Reader.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/StringWriter.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/Writer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Set.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Locale.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/File.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/FilenameFilter.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/PrintStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/ArrayList.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/List.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/regex/Matcher.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/regex/Pattern.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/AccessController.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/PrivilegedAction.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/IllegalAccessException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/InstantiationException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/IllegalArgumentException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/ClassLoader.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Collections.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/LinkedHashMap.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Comparator.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Iterator.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/NoSuchElementException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Iterable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Comparable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/StringBuilder.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Integer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/SortedSet.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/TreeSet.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/StringBuffer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Enum.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Field.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/LinkedList.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/NoSuchFieldException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/CharSequence.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/math/BigInteger.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/BufferedReader.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/EnumMap.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Date.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/text/MessageFormat.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/ResourceBundle.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Cloneable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Boolean.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Number.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Double.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/InputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Collection.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/LinkedHashSet.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/ListIterator.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/text/DateFormat.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/text/SimpleDateFormat.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/TimeZone.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/SimpleTimeZone.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/AbstractCollection.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/AbstractSet.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Map$Entry.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Stack.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Array.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/text/Collator.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/ref/SoftReference.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/UndeclaredThrowableException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/CodeSource.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/Policy.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/PrivilegedActionException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/PrivilegedExceptionAction.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/SecureClassLoader.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/WeakHashMap.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/SecurityManager.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/ByteArrayOutputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/net/URL.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/security/ProtectionDomain.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Documented.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] Note: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/lib/rhino/src/org/mozilla/javascript/commonjs/module/provider/SoftCachingModuleScriptProvider.java uses unchecked or unsafe operations.
    [javac] Note: Recompile with -Xlint:unchecked for details.
    [javac] 100 warnings
     [copy] Copying 2 files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes

compile-jdk15:
    [javac] Compiling 1 source file to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes
    [javac] warning: [options] bootstrap class path not set in conjunction with -source 1.5
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Member.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Method.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Constructor.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Iterator.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Object.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/SecurityException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/InstantiationException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Member.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation': class file for jdk.Profile+Annotation not found
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Method.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Constructor.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Iterator.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Object.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/SecurityException.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/InstantiationException.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Override.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Annotation.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Target.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/ElementType.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Retention.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/RetentionPolicy.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Override.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Annotation.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Target.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/ElementType.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/Retention.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/annotation/RetentionPolicy.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/AutoCloseable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/AutoCloseable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/RuntimeException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/RuntimeException.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Exception.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Exception.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Throwable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Throwable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/ReflectiveOperationException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/ReflectiveOperationException.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Class.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Class.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/NoSuchMethodException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/NoSuchMethodException.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/String.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/String.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Executable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Executable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/AccessibleObject.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/AccessibleObject.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/AnnotatedElement.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/AnnotatedElement.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Iterable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Iterable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Error.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Error.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] 53 warnings

compile:

properties:

compile:
    [javac] Compiling 29 source files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes
    [javac] warning: [options] bootstrap class path not set in conjunction with -source 1.5
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/File.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/FileInputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/IOException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/InputStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/net/MalformedURLException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/net/URL.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/net/URLConnection.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Object.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/String.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/text/MessageFormat.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/PrintStream.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Map.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Throwable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/InterruptedException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JFrame.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/EventQueue.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/ActiveEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/AWTEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/BorderLayout.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Color.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Component.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Container.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Dimension.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Event.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Font.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/FontMetrics.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Frame.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Graphics.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/GridBagConstraints.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/GridBagLayout.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/GridLayout.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/MenuComponent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Point.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Polygon.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Rectangle.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Toolkit.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/List.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/ArrayList.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Arrays.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Collections.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Comparator.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/EventListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/EventObject.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/HashMap.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/util/Properties.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/tree/DefaultTreeCellRenderer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/tree/TreePath.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/reflect/Method.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/WindowConstants.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/accessibility/Accessible.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/RootPaneContainer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/TransferHandler.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/TransferHandler$HasGetTransferHandler.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/Serializable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/MenuContainer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/Window.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/image/ImageObserver.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Runnable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JDesktopPane.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JPanel.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JComponent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/event/ActionListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JMenuBar.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/MenuElement.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JToolBar.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JInternalFrame.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JSplitPane.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JLabel.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JFileChooser.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JMenu.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/event/ActionEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JComboBox.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JTabbedPane.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/event/MouseEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JTable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/TableModelListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/Scrollable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/TableColumnModelListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/ListSelectionListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/CellEditorListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/RowSorterListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/table/AbstractTableModel.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/table/TableModel.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JTextArea.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/text/JTextComponent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/event/KeyListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/DocumentListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JMenuItem.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JCheckBoxMenuItem.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/text/Document.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/text/Segment.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/PopupMenuListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/event/MouseListener.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JScrollPane.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/tree/TreeModel.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/JTree.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/table/TableCellRenderer.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/awt/event/KeyEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/javax/swing/event/DocumentEvent.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] Note: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/lib/rhino/toolsrc/org/mozilla/javascript/tools/debugger/SwingGui.java uses unchecked or unsafe operations.
    [javac] Note: Recompile with -Xlint:unchecked for details.
    [javac] 100 warnings
     [copy] Copying 1 file to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes

xmlimplsrc-compile:
     [echo] Calling /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/lib/rhino/xmlimplsrc/build.xml

compile:

compile-all:

compile:
    [javac] Compiling 3 source files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes
    [javac] warning: [options] bootstrap class path not set in conjunction with -source 1.5
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/RuntimeException.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Exception.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Throwable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/Serializable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Object.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/String.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/RuntimeException.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation': class file for jdk.Profile+Annotation not found
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Exception.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Throwable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/io/Serializable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/Object.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/String.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] warning: /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/AutoCloseable.class): major version 52 is newer than 51, the highest major version supported by this compiler.
    [javac]   It is recommended that the compiler be upgraded.
    [javac] /home/qyh/jdk/jdk8/jdk1.8.0_351/lib/ct.sym(META-INF/sym/rt.jar/java/lang/AutoCloseable.class): warning: Cannot find annotation method 'value()' in type 'Profile+Annotation'
    [javac] 15 warnings

jar:
     [copy] Copying 1 file to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/classes
      [jar] Building jar: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/rhino1_7R5pre/js.jar

rhino-jarjar:
   [jarjar] Building jar: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/rhino.jar

svnversion:

compile:
    [mkdir] Created dir: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/classes
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build.xml:256: warning: 'includeantruntime' was not set, defaulting to build.sysclasspath=last; set to false for repeatable builds
    [javac] Compiling 7 source files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/classes
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build.xml:262: warning: 'includeantruntime' was not set, defaulting to build.sysclasspath=last; set to false for repeatable builds
    [javac] Compiling 390 source files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/classes
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/TypeCheck.java:1015: error: variable obj is already defined in method checkPropCreation(NodeTraversal,Node)
    [javac] Node obj = lvalue.getFirstChild();
    [javac]      ^
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/TypeCheck.java:1016: error: variable prop is already defined in method checkPropCreation(NodeTraversal,Node)
    [javac] Node prop = lvalue.getLastChild();
    [javac]      ^
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/TypeCheck.java:1017: error: variable objType is already defined in method checkPropCreation(NodeTraversal,Node)
    [javac] JSType objType = getJSType(obj);
    [javac]        ^
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/TypeCheck.java:1018: error: variable pname is already defined in method checkPropCreation(NodeTraversal,Node)
    [javac] String pname = prop.getString();
    [javac]        ^
    [javac] Note: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/ant/CompileTask.java uses unchecked or unsafe operations.
    [javac] Note: Recompile with -Xlint:unchecked for details.
    [javac] 4 errors

BUILD FAILED
/home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build.xml:262: Compile failed; see the compiler error output for details.

Total time: 3 seconds
Cannot compile test suite! at /home/qyh/DATASET/defects4j-2.0.1/framework/bin/d4j/d4j-test line 143.
Compilation failed in require at /home/qyh/DATASET/defects4j-2.0.1/framework/bin/defects4j line 195.
"}, ChatCompletionMessage(content="The issue in my last edit is that variable names are redefined (`obj`, `prop`, `objType`, `pname`) within the scope, which conflicts with their existing definitions. I'll revise the logging tool call by removing the redefinitions and directly using the existing variables for inspection.", refusal=None, role='assistant', audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_PFWLXZ6ozbnOR5bdOM98KDDp', function=Function(arguments='{"edits":[{"edit":"<<<<<<< SEARCH\
if (lvalue.isGetProp()) {\
=======\
if (lvalue.isGetProp()) {\
    System.out.println(\\"Debug: Entering checkPropCreation\\");\
    System.out.println(\\"Debug: objType=\\" + getJSType(lvalue.getFirstChild()));\
    System.out.println(\\"Debug: pname=\\" + lvalue.getLastChild().getString());\
    if (getJSType(lvalue.getFirstChild()).isStruct() && !getJSType(lvalue.getFirstChild()).hasProperty(lvalue.getLastChild().getString())) {\
        System.out.println(\\"Debug: objType.isStruct() && !objType.hasProperty(\\" + lvalue.getLastChild().getString() + \\")\\");\
        if (!(lvalue.getFirstChild().isThis() && getJSType(t.getScope().getRootNode()).isConstructor())) {\
          System.out.println(\\"Debug: Triggering report\\");\
          report(t, lvalue.getLastChild(), ILLEGAL_PROPERTY_CREATION);\
        }\
    }\
    return;\
>>>>>>> REPLACE"}],"thought":"Avoid re-declaring variables; instead, directly employ existing variables for logging key values to debug the suspected misclassification issue."}', name='edit_and_run'), type='function')]), {'role': 'tool', 'tool_call_id': 'call_PFWLXZ6ozbnOR5bdOM98KDDp', 'content': "There are errors to compile and run the edited method, please try to re-edit the method.

 Error Log:
Running ant (compile.tests)................................................ FAIL
Executed command:  cd /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166 && /home/qyh/DATASET/defects4j-2.0.1/major/bin/ant -f /home/qyh/DATASET/defects4j-2.0.1/framework/projects/defects4j.build.xml -Dd4j.home=/home/qyh/DATASET/defects4j-2.0.1 -Dd4j.dir.projects=/home/qyh/DATASET/defects4j-2.0.1/framework/projects -Dbasedir=/home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166 -Dbuild.compiler=javac1.7  compile.tests 2>&1
Java HotSpot(TM) 64-Bit Server VM warning: ignoring option MaxPermSize=1G; support was removed in 8.0
Buildfile: /home/qyh/DATASET/defects4j-2.0.1/framework/projects/defects4j.build.xml

rhino:

properties:

init:

compile:

compile-most:

compile-jdk15:

compile:

properties:

compile:

xmlimplsrc-compile:
     [echo] Calling /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/lib/rhino/xmlimplsrc/build.xml

compile:

compile-all:

compile:

jar:

rhino-jarjar:
   [jarjar] Updating jar: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/lib/rhino.jar

svnversion:

compile:
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build.xml:256: warning: 'includeantruntime' was not set, defaulting to build.sysclasspath=last; set to false for repeatable builds
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build.xml:262: warning: 'includeantruntime' was not set, defaulting to build.sysclasspath=last; set to false for repeatable builds
    [javac] Compiling 271 source files to /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build/classes
    [javac] /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/TypeCheck.java:1010: error: unreachable statement
    [javac] Node obj = lvalue.getFirstChild();
    [javac]      ^
    [javac] Note: /home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/src/com/google/javascript/jscomp/ant/CompileTask.java uses unchecked or unsafe operations.
    [javac] Note: Recompile with -Xlint:unchecked for details.
    [javac] 1 error

BUILD FAILED
/home/qyh/projects/FixFL/DebugResult/preprocess/Closure/Closure-4/com_google_javascript_jscomp_TypeCheckTest/testImplementsLoop/round-1/playground-6158348875102156166/build.xml:262: Compile failed; see the compiler error output for details.

Total time: 2 seconds
Cannot compile test suite! at /home/qyh/DATASET/defects4j-2.0.1/framework/bin/d4j/d4j-test line 143.
Compilation failed in require at /home/qyh/DATASET/defects4j-2.0.1/framework/bin/defects4j line 195.
"""

import re


def filter_compile_error(log: str) -> str:
    javac_lines = re.findall(r'\[javac\] .*\n', log)
    javac_warning = r"\[javac\] .*warning: .*\n"
    javac_error = r"(\[javac\] ).*(error: .*)\n"
    javac_note = r"\[javac\] .*Note: .*\n"
    error_lines = []
    flag = False
    for line in javac_lines:
        if re.match(javac_warning, line):
            flag = False
        elif re.match(javac_note, line):
            flag = False
        elif re.match(javac_error, line):
            flag = True
            match = re.match(javac_error, line)
            line = match.group(1) + match.group(2)
        else:
            line = line.strip()
        
        if flag:
            error_lines.append(line)

    return "\n".join(error_lines)