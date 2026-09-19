"""Extra teaching material for the Java lessons (outputs come from real `java` runs)."""
from extra_util import java

EXTRA = {}

EXTRA["java-hello-world"] = {
    "intro": [
        ("h2", "Why Java?"),
        ("p", "Java has been one of the most widely used languages for almost 30 years. It powers Android apps, banking and payment systems, large web backends and huge data platforms. Its design goal was <em>write once, run anywhere</em>: your program is compiled to an intermediate form that any computer with a Java Virtual Machine can run. Java is also <strong>strictly typed</strong>, meaning the compiler checks your code before it ever runs, which catches a whole category of mistakes early. That makes it a demanding first language but an excellent way to learn how programming really works."),
    ],
    "more": [
        ("h2", "What every word in Hello World means"),
        ("p", "Java programs look wordy at first. Here is the smallest program, with each piece explained so none of it stays a mystery:"),
        *java('public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, Java!");\n    }\n}'),
        ("ul", [
            "<code>public class Main</code>: all Java code lives inside a class. The file must be named <code>Main.java</code> to match.",
            "<code>public static void main(String[] args)</code>: the entry point. Java starts running here. <code>void</code> means it returns nothing; <code>args</code> holds any command-line arguments.",
            "<code>System.out.println(...)</code>: prints text followed by a new line. <code>System.out.print</code> omits the new line.",
            "Every statement ends with a semicolon, and blocks are wrapped in curly braces.",
        ]),
        ("h2", "Compile, then run"),
        ("p", "Unlike Python, Java is normally compiled first: <code>javac</code> turns your <code>.java</code> file into <code>.class</code> bytecode, and <code>java</code> runs that bytecode on the JVM. Modern Java (11 and later) can also run a single file directly."),
        ("code", "bash", "javac Main.java     # compile -> creates Main.class\njava Main           # run the bytecode\njava Main.java      # or compile and run a single file in one step"),
        ("h2", "Reading your first compiler error"),
        ("p", "The compiler is strict, and its messages are precise. Forget a semicolon and it tells you the file, the line and the problem."),
        ("code", "text", "Main.java:3: error: ';' expected\n        System.out.println(\"Hello, Java!\")\n                                          ^\n1 error"),
        ("p", "The <code>^</code> marks where Java noticed the problem. Fix that spot and compile again. Because the compiler refuses to build broken code, many bugs never reach a running program."),
        ("h2", "Printing values"),
        *java('public class Main {\n    public static void main(String[] args) {\n        int apples = 3;\n        System.out.println("Apples: " + apples);\n        System.out.println(2 + 3);\n        System.out.println("2 + 3 = " + (2 + 3));\n        System.out.printf("Pi is about %.2f%n", 3.14159);\n    }\n}'),
    ],
    "recap": [
        "Java is compiled to bytecode and runs on the JVM, so the same program runs everywhere.",
        "Code lives in classes; execution starts at <code>public static void main</code>.",
        "Statements end with <code>;</code>, blocks use <code>{ }</code>, and the compiler checks types before running.",
        "<code>javac</code> compiles, <code>java</code> runs; read compiler errors from the file and line number.",
    ],
}

EXTRA["java-variables-types"] = {
    "intro": [
        ("h2", "Every variable has a declared type"),
        ("p", "In Java you must say what <em>kind</em> of value a variable holds when you create it: <code>int count = 5;</code>. The compiler then refuses anything that does not fit, so you cannot accidentally store text in a number. This feels like extra typing at first, but it turns a whole class of runtime surprises into immediate, clear compile errors. Think of variables as labelled containers with a fixed shape: an <code>int</code> box holds whole numbers, a <code>String</code> box holds text."),
    ],
    "more": [
        ("h2", "The everyday types side by side"),
        *java('public class Main {\n    public static void main(String[] args) {\n        int age = 28;\n        long population = 8_000_000_000L;\n        double price = 19.99;\n        boolean active = true;\n        char grade = \'A\';\n        String name = "Ada";\n\n        System.out.println(name + " is " + age + ", grade " + grade);\n        System.out.println(price * 2);\n        System.out.println(population);\n        System.out.println(active);\n    }\n}'),
        ("h2", "Whole-number division surprises everyone once"),
        *java('public class Main {\n    public static void main(String[] args) {\n        System.out.println(7 / 2);          // int / int = int\n        System.out.println(7 / 2.0);        // one double makes it double\n        System.out.println(7 % 2);          // remainder\n        int total = 7, people = 2;\n        double each = (double) total / people;\n        System.out.println(each);\n    }\n}'),
        ("p", "When both operands are <code>int</code>, Java throws away the fraction. Convert one side to <code>double</code> (with a <em>cast</em>) before dividing when you want a decimal answer."),
        ("h2", "Comparing text: equals, not =="),
        ("p", "For objects such as <code>String</code>, <code>==</code> asks \"are these the very same object in memory?\", not \"do they contain the same text?\". Always use <code>.equals()</code>."),
        *java('public class Main {\n    public static void main(String[] args) {\n        String a = "hello";\n        String b = new String("hello");\n        System.out.println(a == b);\n        System.out.println(a.equals(b));\n        System.out.println("Java".equalsIgnoreCase("JAVA"));\n    }\n}'),
        ("h2", "Useful String methods"),
        *java('public class Main {\n    public static void main(String[] args) {\n        String s = "  Hello, World  ";\n        System.out.println(s.trim());\n        System.out.println(s.trim().toUpperCase());\n        System.out.println(s.trim().length());\n        System.out.println(s.contains("World"));\n        System.out.println(s.trim().substring(0, 5));\n        System.out.println(String.join("-", "a", "b", "c"));\n    }\n}'),
    ],
    "recap": [
        "Declare every variable with a type: <code>int</code>, <code>double</code>, <code>boolean</code>, <code>char</code>, <code>String</code>.",
        "Integer division drops the fraction; cast to <code>double</code> for decimals.",
        "Compare strings with <code>.equals()</code>, never <code>==</code>.",
        "The compiler catches type mismatches before your program runs.",
    ],
}

EXTRA["java-control-flow"] = {
    "intro": [
        ("h2", "Decisions and repetition"),
        ("p", "Control flow is how a program chooses what to do next and how it repeats work. Java uses the same building blocks as most languages: <code>if</code>/<code>else</code> to decide, <code>switch</code> to pick among many fixed options, and <code>for</code>/<code>while</code> loops to repeat. Blocks are wrapped in curly braces (indentation is only for humans), so a missing brace is a classic beginner error."),
    ],
    "more": [
        ("h2", "if / else if / else, traced"),
        *java('public class Main {\n    public static void main(String[] args) {\n        int score = 78;\n\n        if (score >= 90) {\n            System.out.println("A");\n        } else if (score >= 75) {\n            System.out.println("B");\n        } else {\n            System.out.println("C");\n        }\n\n        boolean passed = score >= 50 && score <= 100;\n        System.out.println("passed = " + passed);\n    }\n}'),
        ("h2", "The classic loops"),
        *java('public class Main {\n    public static void main(String[] args) {\n        for (int i = 1; i <= 3; i++) {\n            System.out.println("round " + i);\n        }\n\n        int n = 3;\n        while (n > 0) {\n            System.out.println("countdown " + n);\n            n--;\n        }\n\n        String[] names = {"Ada", "Linus", "Grace"};\n        for (String name : names) {\n            System.out.println("Hi " + name);\n        }\n    }\n}'),
        ("p", "A <code>for</code> loop has three parts in its parentheses: start (<code>int i = 1</code>), keep-going test (<code>i &lt;= 3</code>) and step (<code>i++</code>). The <em>enhanced for</em> loop at the end reads as \"for each name in names\" and is the cleanest way to walk an array or list."),
        ("h2", "switch for many fixed choices"),
        *java('public class Main {\n    public static void main(String[] args) {\n        String day = "SAT";\n        String type = switch (day) {\n            case "SAT", "SUN" -> "weekend";\n            case "MON", "TUE", "WED", "THU", "FRI" -> "weekday";\n            default -> "unknown";\n        };\n        System.out.println(day + " is a " + type);\n    }\n}'),
        ("h2", "Worked example: sum and average"),
        *java('public class Main {\n    public static void main(String[] args) {\n        int[] scores = {72, 88, 95, 61};\n        int sum = 0;\n        for (int s : scores) {\n            sum += s;\n        }\n        double average = (double) sum / scores.length;\n        System.out.println("sum = " + sum);\n        System.out.println("average = " + average);\n    }\n}'),
    ],
    "recap": [
        "<code>if</code>/<code>else if</code>/<code>else</code> decide; conditions must be <code>boolean</code>.",
        "<code>for</code>, enhanced <code>for</code> and <code>while</code> repeat work; watch off-by-one errors.",
        "Modern <code>switch</code> with <code>-&gt;</code> is a compact way to map values to results.",
        "Always use braces, even for one-line bodies.",
    ],
}

EXTRA["java-oop-classes"] = {
    "intro": [
        ("h2", "Objects model real things"),
        ("p", "Java is built around <strong>object-oriented programming</strong>. Rather than a long list of separate variables and functions, you describe a kind of thing once as a <em>class</em> (its data and its abilities) and then create as many <em>objects</em> from it as you need. A <code>BankAccount</code> class describes what every account has (an owner, a balance) and can do (deposit, withdraw). Each customer's account is a separate object with its own numbers."),
    ],
    "more": [
        ("h2", "A class, an object, and encapsulation"),
        *java('class BankAccount {\n    private final String owner;\n    private double balance;\n\n    BankAccount(String owner, double balance) {\n        this.owner = owner;\n        this.balance = balance;\n    }\n\n    void deposit(double amount) {\n        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");\n        balance += amount;\n    }\n\n    double getBalance() { return balance; }\n    String getOwner() { return owner; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        BankAccount a = new BankAccount("Ada", 100);\n        BankAccount b = new BankAccount("Linus", 50);\n        a.deposit(25);\n        System.out.println(a.getOwner() + ": " + a.getBalance());\n        System.out.println(b.getOwner() + ": " + b.getBalance());\n    }\n}'),
        ("ul", [
            "<code>private</code> fields can only be touched from inside the class. This is <strong>encapsulation</strong>: outsiders must go through methods, so the class can enforce its rules (no negative deposits).",
            "The <em>constructor</em> has the class name and no return type; it runs when you write <code>new BankAccount(...)</code>.",
            "<code>this</code> refers to the object being built or used, and disambiguates fields from parameters.",
            "Each <code>new</code> creates an independent object: depositing into <code>a</code> never changes <code>b</code>.",
        ]),
        ("h2", "Inheritance and polymorphism"),
        *java('class Animal {\n    String speak() { return "..."; }\n}\n\nclass Dog extends Animal {\n    @Override\n    String speak() { return "Woof"; }\n}\n\nclass Cat extends Animal {\n    @Override\n    String speak() { return "Meow"; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        Animal[] pets = { new Dog(), new Cat(), new Animal() };\n        for (Animal p : pets) {\n            System.out.println(p.speak());\n        }\n    }\n}'),
        ("p", "The loop only knows about <code>Animal</code>, yet each object answers in its own way. That is <strong>polymorphism</strong>: the same call, different behaviour depending on the real object. It lets you add a new kind of animal without changing the loop."),
        ("h2", "Interfaces: promises about behaviour"),
        *java('interface Shape {\n    double area();\n}\n\nrecord Circle(double r) implements Shape {\n    public double area() { return Math.PI * r * r; }\n}\n\nrecord Rect(double w, double h) implements Shape {\n    public double area() { return w * h; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        Shape[] shapes = { new Circle(1), new Rect(3, 4) };\n        for (Shape s : shapes) {\n            System.out.printf("%.2f%n", s.area());\n        }\n    }\n}'),
    ],
    "recap": [
        "A class is a blueprint; <code>new</code> makes independent objects from it.",
        "Keep fields <code>private</code> and expose behaviour through methods (encapsulation).",
        "Subclasses <code>extend</code> and <code>@Override</code>; interfaces declare what a class can do.",
        "Polymorphism lets code work with the general type while objects behave as their real type.",
    ],
}

EXTRA["java-collections"] = {
    "intro": [
        ("h2", "Arrays are fixed, collections grow"),
        ("p", "A plain array has a size that never changes. Real programs constantly add and remove items, look things up and remove duplicates. The Java <strong>Collections Framework</strong> provides ready-made containers for these jobs. The three you will use most: <code>List</code> (ordered, allows duplicates), <code>Set</code> (no duplicates) and <code>Map</code> (key to value, like a dictionary)."),
    ],
    "more": [
        ("h2", "List: an ordered, growable sequence"),
        *java('import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        List<String> tasks = new ArrayList<>();\n        tasks.add("write");\n        tasks.add("test");\n        tasks.add("ship");\n        tasks.remove("test");\n\n        System.out.println(tasks);\n        System.out.println(tasks.size() + " tasks, first = " + tasks.get(0));\n        System.out.println(tasks.contains("ship"));\n    }\n}'),
        ("p", "The <code>&lt;String&gt;</code> is a <em>generic</em>: it tells the compiler this list only holds strings, so adding a number is a compile error."),
        ("h2", "Set: uniqueness for free"),
        *java('import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Set<String> tags = new TreeSet<>();\n        tags.add("java");\n        tags.add("sql");\n        tags.add("java");        // duplicate ignored\n        System.out.println(tags);\n        System.out.println(tags.size());\n    }\n}'),
        ("h2", "Map: look things up by key"),
        *java('import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Map<String, Integer> stock = new TreeMap<>();\n        stock.put("apple", 5);\n        stock.put("pear", 2);\n        stock.merge("apple", 3, Integer::sum);   // add to existing\n\n        for (Map.Entry<String, Integer> e : stock.entrySet()) {\n            System.out.println(e.getKey() + " -> " + e.getValue());\n        }\n        System.out.println(stock.getOrDefault("kiwi", 0));\n    }\n}'),
        ("h2", "Worked example: count word frequency"),
        *java('import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        String text = "the cat and the hat and the bat";\n        Map<String, Integer> counts = new TreeMap<>();\n        for (String w : text.split(" ")) {\n            counts.merge(w, 1, Integer::sum);\n        }\n        System.out.println(counts);\n    }\n}'),
    ],
    "recap": [
        "<code>List</code> keeps order and allows duplicates; <code>Set</code> rejects duplicates; <code>Map</code> stores key-value pairs.",
        "Generics like <code>List&lt;String&gt;</code> make the compiler check element types.",
        "Program to the interface (<code>List</code>) and choose the implementation (<code>ArrayList</code>) on the right.",
        "<code>Map.merge</code> is a neat way to count things.",
    ],
}

EXTRA["java-exceptions"] = {
    "intro": [
        ("h2", "When things go wrong"),
        ("p", "Files are missing, numbers arrive as text, networks fail. An <strong>exception</strong> is Java's way of saying \"something went wrong here\" and unwinding until some code decides how to handle it. Without handling, the program prints a stack trace and stops. With <code>try</code>/<code>catch</code> you keep control and respond sensibly, for example by showing a friendly message or trying again."),
    ],
    "more": [
        ("h2", "Catching a specific exception"),
        *java('public class Main {\n    public static void main(String[] args) {\n        String[] inputs = {"42", "abc", "7"};\n        for (String s : inputs) {\n            try {\n                int n = Integer.parseInt(s);\n                System.out.println("parsed " + n);\n            } catch (NumberFormatException e) {\n                System.out.println("not a number: " + s);\n            } finally {\n                System.out.println("(done with " + s + ")");\n            }\n        }\n    }\n}'),
        ("p", "The loop keeps going after the bad input; the exception was contained. <code>finally</code> runs whether or not an exception happened, which is the right place for cleanup."),
        ("h2", "Reading a stack trace"),
        ("p", "An uncaught exception prints where it started and how the program got there. Read the first line (the type and message) and then the first line that mentions <em>your</em> code."),
        ("code", "text", "Exception in thread \"main\" java.lang.ArithmeticException: / by zero\n\tat Main.divide(Main.java:4)\n\tat Main.main(Main.java:9)"),
        ("h2", "Throwing an exception with a clear message"),
        *java('public class Main {\n    static double average(int[] nums) {\n        if (nums.length == 0) {\n            throw new IllegalArgumentException("need at least one number");\n        }\n        int sum = 0;\n        for (int n : nums) sum += n;\n        return (double) sum / nums.length;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(average(new int[]{2, 4, 6}));\n        try {\n            average(new int[]{});\n        } catch (IllegalArgumentException e) {\n            System.out.println("Error: " + e.getMessage());\n        }\n    }\n}'),
        ("h2", "Checked versus unchecked, in plain words"),
        ("ul", [
            "<strong>Checked</strong> exceptions (such as <code>IOException</code>) are things the compiler forces you to deal with, because they can happen even in correct code (a file may be missing).",
            "<strong>Unchecked</strong> exceptions (such as <code>NullPointerException</code>) usually mean a bug in the code; you fix the code rather than catch them everywhere.",
        ]),
        ("h2", "Letting Java close resources for you"),
        ("code", "java", "try (BufferedReader reader = new BufferedReader(new FileReader(\"data.txt\"))) {\n    System.out.println(reader.readLine());\n} catch (IOException e) {\n    System.out.println(\"could not read file: \" + e.getMessage());\n}\n// the reader is closed automatically, even if an exception was thrown"),
    ],
    "recap": [
        "Wrap risky code in <code>try</code> and catch the <em>specific</em> exception you expect.",
        "<code>finally</code> always runs; try-with-resources closes files and connections automatically.",
        "Throw your own exceptions with clear messages when input is invalid.",
        "Read stack traces top-down: type and message first, then the first line of your own code.",
    ],
}
