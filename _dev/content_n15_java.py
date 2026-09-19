"""Java lessons 7-15."""
from content_js_sql import M

META = [
    M("java-strings", "java", "Strings and StringBuilder", 12, "Beginner", "Immutable strings, common methods, comparison and building text efficiently.", ["Use core String methods", "Compare with equals", "Build text with StringBuilder"]),
    M("java-arrays", "java", "Arrays", 12, "Beginner", "Fixed-size arrays, loops over them, 2D arrays and the Arrays utility class.", ["Create and index arrays", "Loop with for and for-each", "Sort and print with Arrays"]),
    M("java-methods", "java", "Methods and Overloading", 12, "Beginner", "Parameters, return values, overloading, varargs and pass-by-value.", ["Write methods with return types", "Overload a method", "Explain pass-by-value"]),
    M("java-inheritance", "java", "Inheritance and Polymorphism", 15, "Intermediate", "extends, super, overriding and treating subclasses as their parent type.", ["Extend a class", "Override methods", "Use polymorphism"]),
    M("java-interfaces-abstract", "java", "Interfaces and Abstract Classes", 14, "Intermediate", "Contracts, default methods and when to choose an interface or an abstract class.", ["Define an interface", "Write an abstract class", "Choose between them"]),
    M("java-generics", "java", "Generics", 14, "Intermediate", "Type-safe containers and methods with type parameters and bounds.", ["Write a generic class", "Write a generic method", "Use bounded types"]),
    M("java-lambdas-streams", "java", "Lambdas and Streams", 16, "Intermediate", "Functional interfaces, lambdas, method references and the Stream pipeline.", ["Write lambdas", "Filter, map and collect", "Use Optional safely"]),
    M("java-files-io", "java", "Files and I/O", 14, "Intermediate", "Read and write files with java.nio and handle resources with try-with-resources.", ["Read and write text files", "Use try-with-resources", "Work with Path"]),
    M("java-testing-junit", "java", "Testing with JUnit", 14, "Intermediate", "Write unit tests, assertions and run them with Maven or Gradle.", ["Write a JUnit 5 test", "Use assertions", "Test exceptions"]),
]

CONTENT = {}

CONTENT["java-strings"] = [
    ("p", "A <code>String</code> is a sequence of characters. In Java strings are <strong>immutable</strong>: every operation that seems to change one actually returns a new string, and the original stays untouched."),
    ("h2", "Everyday methods"),
    ("code", "java", 'public class Main {\n    public static void main(String[] args) {\n        String s = "  Hello, Java  ";\n        System.out.println(s.trim());\n        System.out.println(s.toUpperCase());\n        System.out.println(s.length());\n        System.out.println(s.trim().substring(0, 5));\n        System.out.println(s.contains("Java"));\n        System.out.println(s.replace("Java", "World").trim());\n    }\n}'),
    ("output", "Hello, Java\n  HELLO, JAVA  \n15\nHello\ntrue\nHello, World"),
    ("h2", "Comparing strings"),
    ("p", "Never compare strings with <code>==</code>. It checks whether two variables point at the same object, not whether the text matches. Use <code>equals</code>."),
    ("code", "java", 'public class Main {\n    public static void main(String[] args) {\n        String a = new String("hi");\n        String b = new String("hi");\n        System.out.println(a == b);\n        System.out.println(a.equals(b));\n        System.out.println("Hi".equalsIgnoreCase("hI"));\n    }\n}'),
    ("output", "false\ntrue\ntrue"),
    ("h2", "Splitting, joining and formatting"),
    ("code", "java", 'public class Main {\n    public static void main(String[] args) {\n        String[] parts = "a,b,c".split(",");\n        System.out.println(parts.length);\n        System.out.println(String.join("-", parts));\n        System.out.println(String.format("%s scored %d (%.1f%%)", "Ada", 42, 93.456));\n    }\n}'),
    ("output", "3\na-b-c\nAda scored 42 (93.5%)"),
    ("h2", "StringBuilder"),
    ("p", "Because strings are immutable, gluing many pieces in a loop with <code>+</code> creates many throwaway objects. <code>StringBuilder</code> is a mutable buffer built for this."),
    ("code", "java", 'public class Main {\n    public static void main(String[] args) {\n        StringBuilder sb = new StringBuilder();\n        for (int i = 1; i <= 5; i++) {\n            sb.append(i).append(\' \');\n        }\n        System.out.println(sb.toString().trim());\n        System.out.println(sb.reverse().toString().trim());\n    }\n}'),
    ("output", "1 2 3 4 5\n5 4 3 2 1"),
    ("note", "Text blocks", "Multi-line text can use triple quotes: <code>\"\"\"</code> ... <code>\"\"\"</code> (Java 15+), which keeps line breaks and avoids escaping quotes."),
    ("exercise", "Write a method that returns true if a string is a palindrome, ignoring case and spaces (use StringBuilder.reverse)."),
]

CONTENT["java-arrays"] = [
    ("p", "An array holds a <strong>fixed number</strong> of values of one type, stored side by side and accessed by index starting at 0. The length is set when you create it and cannot change."),
    ("h2", "Creating and reading"),
    ("code", "java", 'public class Main {\n    public static void main(String[] args) {\n        int[] scores = new int[3];      // {0, 0, 0}\n        scores[0] = 90;\n        int[] primes = {2, 3, 5, 7};\n        System.out.println(scores[0] + " " + primes.length);\n        System.out.println(primes[primes.length - 1]);\n    }\n}'),
    ("output", "90 4\n7"),
    ("p", "Reading past the end throws <code>ArrayIndexOutOfBoundsException</code>; valid indexes are <code>0</code> to <code>length - 1</code>."),
    ("h2", "Looping"),
    ("code", "java", 'public class Main {\n    public static void main(String[] args) {\n        int[] nums = {4, 8, 15};\n        int sum = 0;\n        for (int n : nums) {\n            sum += n;\n        }\n        System.out.println(sum);\n        for (int i = 0; i < nums.length; i++) {\n            System.out.println(i + ": " + nums[i]);\n        }\n    }\n}'),
    ("output", "27\n0: 4\n1: 8\n2: 15"),
    ("h2", "The Arrays helper class"),
    ("code", "java", 'import java.util.Arrays;\n\npublic class Main {\n    public static void main(String[] args) {\n        int[] a = {5, 2, 9, 1};\n        Arrays.sort(a);\n        System.out.println(Arrays.toString(a));\n        System.out.println(Arrays.binarySearch(a, 5));\n        int[] copy = Arrays.copyOf(a, 6);\n        System.out.println(Arrays.toString(copy));\n        System.out.println(Arrays.equals(a, copy));\n    }\n}'),
    ("output", "[1, 2, 5, 9]\n2\n[1, 2, 5, 9, 0, 0]\nfalse"),
    ("note", "Printing", "<code>System.out.println(array)</code> prints something like <code>[I@1b6d3586</code>. Use <code>Arrays.toString</code> (or <code>deepToString</code> for nested arrays)."),
    ("h2", "Two-dimensional arrays"),
    ("code", "java", 'import java.util.Arrays;\n\npublic class Main {\n    public static void main(String[] args) {\n        int[][] grid = {{1, 2, 3}, {4, 5, 6}};\n        System.out.println(grid[1][2]);\n        System.out.println(Arrays.deepToString(grid));\n    }\n}'),
    ("output", "6\n[[1, 2, 3], [4, 5, 6]]"),
    ("exercise", "Write a method that returns the largest value in an int[] without using Arrays.sort."),
]

CONTENT["java-methods"] = [
    ("p", "A method is a named block of code you can call again and again. It declares what it takes in (parameters) and what it gives back (return type), or <code>void</code> if nothing."),
    ("h2", "Parameters and return values"),
    ("code", "java", 'public class Main {\n    static int square(int n) {\n        return n * n;\n    }\n\n    static void greet(String name) {\n        System.out.println("Hi " + name);\n    }\n\n    public static void main(String[] args) {\n        greet("Ada");\n        System.out.println(square(7));\n    }\n}'),
    ("output", "Hi Ada\n49"),
    ("h2", "Overloading"),
    ("p", "Several methods can share a name if their parameter lists differ. The compiler picks the one that matches the call."),
    ("code", "java", 'public class Main {\n    static int add(int a, int b) { return a + b; }\n    static double add(double a, double b) { return a + b; }\n    static int add(int a, int b, int c) { return a + b + c; }\n\n    public static void main(String[] args) {\n        System.out.println(add(1, 2));\n        System.out.println(add(1.5, 2.5));\n        System.out.println(add(1, 2, 3));\n    }\n}'),
    ("output", "3\n4.0\n6"),
    ("h2", "Varargs"),
    ("code", "java", 'public class Main {\n    static int sum(int... nums) {\n        int total = 0;\n        for (int n : nums) total += n;\n        return total;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(sum());\n        System.out.println(sum(1, 2, 3, 4));\n    }\n}'),
    ("output", "0\n10"),
    ("h2", "Java is always pass-by-value"),
    ("p", "A method receives a <em>copy</em> of each argument. For primitives that copy is the number itself, so changing it does nothing to the caller. For objects the copy is the <em>reference</em>: the method can change the object's contents, but reassigning the parameter does not affect the caller's variable."),
    ("code", "java", 'public class Main {\n    static void change(int n, StringBuilder sb) {\n        n = 99;\n        sb.append("!");\n        sb = new StringBuilder("other");\n    }\n\n    public static void main(String[] args) {\n        int n = 1;\n        StringBuilder sb = new StringBuilder("hey");\n        change(n, sb);\n        System.out.println(n + " " + sb);\n    }\n}'),
    ("output", "1 hey!"),
    ("exercise", "Write an overloaded <code>max</code> that works for two ints, two doubles and an int array."),
]

CONTENT["java-inheritance"] = [
    ("p", "Inheritance lets a class reuse and extend another. The child (subclass) gets the parent's (superclass's) fields and methods and can add or replace behaviour. Model an <strong>is-a</strong> relationship: a Dog <em>is an</em> Animal."),
    ("h2", "extends and super"),
    ("code", "java", 'class Animal {\n    protected String name;\n    Animal(String name) { this.name = name; }\n    String sound() { return "..."; }\n    public String toString() { return name + " says " + sound(); }\n}\n\nclass Dog extends Animal {\n    Dog(String name) { super(name); }   // call the parent constructor\n    @Override\n    String sound() { return "Woof"; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(new Dog("Rex"));\n        System.out.println(new Animal("Thing"));\n    }\n}'),
    ("output", "Rex says Woof\nThing says ..."),
    ("h2", "Polymorphism"),
    ("p", "A variable of the parent type can hold any subclass. Java calls the <em>actual</em> object's version of an overridden method at runtime."),
    ("code", "java", 'class Animal { String sound() { return "..."; } }\nclass Dog extends Animal { String sound() { return "Woof"; } }\nclass Cat extends Animal { String sound() { return "Meow"; } }\n\npublic class Main {\n    public static void main(String[] args) {\n        Animal[] zoo = { new Dog(), new Cat(), new Animal() };\n        for (Animal a : zoo) {\n            System.out.println(a.sound());\n        }\n    }\n}'),
    ("output", "Woof\nMeow\n..."),
    ("h2", "Rules worth remembering"),
    ("ul", [
        "A class can extend only <strong>one</strong> class (single inheritance).",
        "Add <code>@Override</code> so the compiler catches typos in method names.",
        "<code>final</code> on a class or method forbids extending or overriding it.",
        "Every class extends <code>Object</code>, which is where <code>toString</code>, <code>equals</code> and <code>hashCode</code> come from.",
    ]),
    ("note", "Prefer composition", "If the relationship is not truly is-a, hold the other class as a field instead. A Car <em>has an</em> Engine; it is not one."),
    ("exercise", "Create Shape with an abstract-style <code>area()</code> returning 0, then Circle and Rectangle that override it. Print the areas from a Shape[]."),
]

CONTENT["java-interfaces-abstract"] = [
    ("p", "Both interfaces and abstract classes describe what a type can do without fixing every detail. They solve slightly different problems."),
    ("h2", "Interfaces: a contract"),
    ("code", "java", 'interface Payable {\n    double amount();\n    default String receipt() {          // optional shared behaviour\n        return "Pay " + amount();\n    }\n}\n\nclass Invoice implements Payable {\n    public double amount() { return 250.0; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        Payable p = new Invoice();\n        System.out.println(p.receipt());\n    }\n}'),
    ("output", "Pay 250.0"),
    ("p", "A class may implement <strong>many</strong> interfaces. Interface methods are public by default and interfaces hold no instance state."),
    ("h2", "Abstract classes: a partial implementation"),
    ("code", "java", 'abstract class Report {\n    void print() {                     // template shared by all reports\n        System.out.println("== " + title() + " ==");\n        System.out.println(body());\n    }\n    abstract String title();\n    abstract String body();\n}\n\nclass Sales extends Report {\n    String title() { return "Sales"; }\n    String body() { return "Up 12%"; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        new Sales().print();\n    }\n}'),
    ("output", "== Sales ==\nUp 12%"),
    ("p", "You cannot create an instance of an abstract class. It can have fields, constructors and concrete methods."),
    ("h2", "Which one?"),
    ("ul", [
        "Use an <strong>interface</strong> to say what something can do (<code>Comparable</code>, <code>Runnable</code>), especially across unrelated classes.",
        "Use an <strong>abstract class</strong> when related classes share state or code and you want to force subclasses to fill the gaps.",
        "When unsure, start with an interface; it is more flexible.",
    ]),
    ("exercise", "Define an interface <code>Discount</code> with <code>double apply(double price)</code> and implement it as percent-off and flat-off classes."),
]

CONTENT["java-generics"] = [
    ("p", "Generics let a class or method work with a type chosen by the caller while the compiler still checks it. That is why <code>List&lt;String&gt;</code> will not let you add an <code>int</code>."),
    ("h2", "A generic class"),
    ("code", "java", 'class Box<T> {\n    private T value;\n    Box(T value) { this.value = value; }\n    T get() { return value; }\n}\n\npublic class Main {\n    public static void main(String[] args) {\n        Box<String> s = new Box<>("hello");\n        Box<Integer> n = new Box<>(42);\n        String text = s.get();       // no cast needed\n        System.out.println(text + " " + (n.get() + 1));\n    }\n}'),
    ("output", "hello 43"),
    ("h2", "A generic method"),
    ("code", "java", 'import java.util.List;\n\npublic class Main {\n    static <T> T firstOrNull(List<T> items) {\n        return items.isEmpty() ? null : items.get(0);\n    }\n\n    public static void main(String[] args) {\n        System.out.println(firstOrNull(List.of("a", "b")));\n        System.out.println(firstOrNull(List.<Integer>of()));\n    }\n}'),
    ("output", "a\nnull"),
    ("h2", "Bounded types"),
    ("p", "Restrict a type parameter with <code>extends</code> to use the methods of that type."),
    ("code", "java", 'import java.util.List;\n\npublic class Main {\n    static <T extends Comparable<T>> T max(List<T> items) {\n        T best = items.get(0);\n        for (T x : items) {\n            if (x.compareTo(best) > 0) best = x;\n        }\n        return best;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(max(List.of(3, 9, 4)));\n        System.out.println(max(List.of("pear", "apple", "zebra")));\n    }\n}'),
    ("output", "9\nzebra"),
    ("h2", "Limits to know"),
    ("ul", [
        "Type parameters must be <strong>objects</strong>: use <code>Integer</code>, not <code>int</code>.",
        "Generics are erased at runtime, so you cannot do <code>new T()</code> or <code>instanceof List&lt;String&gt;</code>.",
        "<code>List&lt;Dog&gt;</code> is not a <code>List&lt;Animal&gt;</code>; use wildcards like <code>List&lt;? extends Animal&gt;</code> for read-only flexibility.",
    ]),
    ("exercise", "Write a generic <code>Pair&lt;A, B&gt;</code> class with getters and a <code>swap()</code> method returning <code>Pair&lt;B, A&gt;</code>."),
]

CONTENT["java-lambdas-streams"] = [
    ("p", "A <strong>lambda</strong> is a short anonymous function. It can be used wherever Java expects a <em>functional interface</em>: an interface with a single abstract method, such as <code>Runnable</code>, <code>Comparator</code> or <code>Function</code>."),
    ("h2", "Lambdas and method references"),
    ("code", "java", 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        List<String> names = new ArrayList<>(List.of("Grace", "Al", "Linus"));\n        names.sort((a, b) -> a.length() - b.length());\n        System.out.println(names);\n        names.forEach(System.out::println);   // method reference\n    }\n}'),
    ("output", "[Al, Grace, Linus]\nAl\nGrace\nLinus"),
    ("h2", "Stream pipelines"),
    ("p", "A stream takes data through steps: a source, zero or more <strong>intermediate</strong> operations (filter, map, sorted) and one <strong>terminal</strong> operation (collect, count, sum) that actually runs it. The source list is never modified."),
    ("code", "java", 'import java.util.*;\nimport java.util.stream.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        List<Integer> nums = List.of(1, 2, 3, 4, 5, 6);\n        List<Integer> evenSquares = nums.stream()\n            .filter(n -> n % 2 == 0)\n            .map(n -> n * n)\n            .collect(Collectors.toList());\n        System.out.println(evenSquares);\n        System.out.println(nums.stream().mapToInt(Integer::intValue).sum());\n        System.out.println(nums.stream().anyMatch(n -> n > 5));\n    }\n}'),
    ("output", "[4, 16, 36]\n21\ntrue"),
    ("h2", "Grouping"),
    ("code", "java", 'import java.util.*;\nimport java.util.stream.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        List<String> words = List.of("apple", "avocado", "banana", "blueberry", "cherry");\n        Map<Character, List<String>> byLetter = words.stream()\n            .collect(Collectors.groupingBy(w -> w.charAt(0)));\n        System.out.println(byLetter);\n    }\n}'),
    ("output", "{a=[apple, avocado], b=[banana, blueberry], c=[cherry]}"),
    ("h2", "Optional"),
    ("p", "<code>Optional&lt;T&gt;</code> makes \"there may be no value\" explicit, so callers cannot forget the empty case."),
    ("code", "java", 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Optional<String> first = List.of("x", "yy").stream().filter(s -> s.length() > 5).findFirst();\n        System.out.println(first.orElse("none"));\n        System.out.println(first.isPresent());\n    }\n}'),
    ("output", "none\nfalse"),
    ("exercise", "From a list of names, produce the upper-cased names longer than 3 letters, sorted alphabetically, joined with commas (Collectors.joining)."),
]

CONTENT["java-files-io"] = [
    ("p", "Modern Java reads and writes files through <code>java.nio.file</code>: <code>Path</code> describes a location and <code>Files</code> does the work. Most methods throw <code>IOException</code>, which you must catch or declare."),
    ("h2", "Write and read a text file"),
    ("code", "java", 'import java.io.IOException;\nimport java.nio.file.*;\nimport java.util.List;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        Path file = Path.of("notes.txt");\n        Files.writeString(file, "first\\nsecond\\nthird\\n");\n        List<String> lines = Files.readAllLines(file);\n        System.out.println(lines.size() + " lines");\n        System.out.println(lines.get(1));\n        Files.delete(file);\n    }\n}'),
    ("output", "3 lines\nsecond"),
    ("h2", "Big files: stream lines"),
    ("p", "<code>readAllLines</code> loads everything into memory. For large files read line by line with a <code>BufferedReader</code>."),
    ("code", "java", 'import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        try (BufferedReader in = new BufferedReader(new FileReader("data.txt"))) {\n            String line;\n            while ((line = in.readLine()) != null) {\n                System.out.println(line);\n            }\n        }\n    }\n}'),
    ("h2", "try-with-resources"),
    ("p", "Anything that implements <code>AutoCloseable</code> declared in the <code>try (...)</code> parentheses is closed automatically, even if an exception is thrown. It replaces a manual <code>finally</code> block."),
    ("h2", "Working with paths"),
    ("code", "java", 'import java.nio.file.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Path p = Path.of("data", "2025", "report.csv");\n        System.out.println(p);\n        System.out.println(p.getFileName());\n        System.out.println(p.getParent());\n        System.out.println(Files.exists(p));\n    }\n}'),
    ("output", "data/2025/report.csv\nreport.csv\ndata/2025\nfalse"),
    ("note", "Path separators", "Build paths with <code>Path.of(a, b, c)</code> instead of concatenating strings so the code works on Windows and Unix."),
    ("exercise", "Write a program that counts the words in a text file and prints the total."),
]

CONTENT["java-testing-junit"] = [
    ("p", "A unit test calls a small piece of code with known input and checks the result. <strong>JUnit 5</strong> is the standard framework: it finds methods annotated with <code>@Test</code>, runs them and reports which failed."),
    ("h2", "Setup"),
    ("p", "With Maven, add JUnit Jupiter and put tests under <code>src/test/java</code>."),
    ("code", "bash", "<!-- pom.xml -->\n<dependency>\n  <groupId>org.junit.jupiter</groupId>\n  <artifactId>junit-jupiter</artifactId>\n  <version>5.10.2</version>\n  <scope>test</scope>\n</dependency>\n\n# run\nmvn test"),
    ("h2", "Your first test"),
    ("code", "java", 'import org.junit.jupiter.api.Test;\nimport static org.junit.jupiter.api.Assertions.*;\n\nclass Calculator {\n    int add(int a, int b) { return a + b; }\n    int divide(int a, int b) { return a / b; }\n}\n\nclass CalculatorTest {\n    private final Calculator calc = new Calculator();\n\n    @Test\n    void addsTwoNumbers() {\n        assertEquals(5, calc.add(2, 3));\n    }\n\n    @Test\n    void divisionByZeroThrows() {\n        assertThrows(ArithmeticException.class, () -> calc.divide(1, 0));\n    }\n}'),
    ("h2", "Common assertions"),
    ("ul", [
        "<code>assertEquals(expected, actual)</code>: note the order, expected first.",
        "<code>assertTrue</code> / <code>assertFalse</code> for conditions.",
        "<code>assertNull</code> / <code>assertNotNull</code>.",
        "<code>assertThrows</code> checks that code raises the exception you expect.",
    ]),
    ("h2", "Lifecycle and parameterised tests"),
    ("code", "java", 'import org.junit.jupiter.api.*;\nimport org.junit.jupiter.params.ParameterizedTest;\nimport org.junit.jupiter.params.provider.CsvSource;\nimport static org.junit.jupiter.api.Assertions.assertEquals;\n\nclass MathTest {\n    @BeforeEach\n    void setUp() { /* runs before every test */ }\n\n    @ParameterizedTest\n    @CsvSource({"1,1,2", "2,3,5", "10,-4,6"})\n    void adds(int a, int b, int expected) {\n        assertEquals(expected, a + b);\n    }\n}'),
    ("note", "Good tests", "Name tests for behaviour (<code>divisionByZeroThrows</code>), keep one idea per test, and make them independent so they pass in any order."),
    ("exercise", "Write tests for a <code>isPalindrome(String)</code> method covering empty string, one letter, mixed case and a non-palindrome."),
]
