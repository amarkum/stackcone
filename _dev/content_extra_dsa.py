"""Extra teaching material for Data Structures and Algorithms (Python examples, real output)."""
from extra_util import py

EXTRA = {}

EXTRA["ds-introduction"] = {
    "intro": [
        ("h2", "Organising data is a design decision"),
        ("p", "Imagine a library. If books are thrown into one giant pile, finding a title means checking every book. If they are shelved alphabetically, you can jump straight to the right shelf. The books did not change, only how they are <em>organised</em>, and the speed of finding one changed enormously. A <strong>data structure</strong> is a way of organising data in memory so that the operations you care about (add, find, remove, order) are fast."),
        ("p", "There is no single best structure. Each one is good at some operations and worse at others, so choosing well is a skill. That skill is what interviews test and what makes real programs fast."),
    ],
    "more": [
        ("h2", "The same task, three structures"),
        ("p", "Suppose you need to check whether a username is taken. Watch how the choice of structure changes the work, even though the answer is identical."),
        *py('import time\n\nnames_list = [f"user{i}" for i in range(200_000)]\nnames_set = set(names_list)\n\ntarget = "user199999"          # worst case for the list\n\nt = time.perf_counter()\nfound_list = target in names_list       # scans item by item\nlist_time = time.perf_counter() - t\n\nt = time.perf_counter()\nfound_set = target in names_set         # jumps straight to the answer\nset_time = time.perf_counter() - t\n\nprint(found_list, found_set)\nprint("set is faster:", set_time < list_time)'),
        ("p", "Both return <code>True</code>, but the list looked at up to 200,000 items while the set went almost directly to the answer. That gap grows with the data, which is why this matters."),
        ("h2", "How to choose: three questions"),
        ("ul", [
            "<strong>What do I do most?</strong> Look things up by key (hash table), keep things sorted (tree), process in arrival order (queue), undo steps (stack)?",
            "<strong>Does the order matter?</strong> Lists keep order; sets do not.",
            "<strong>Do duplicates matter?</strong> Sets remove them; lists keep them.",
        ]),
        ("h2", "A first mapping to real problems"),
        ("ul", [
            "Browser <em>back</em> button → <strong>stack</strong>.",
            "Print jobs waiting their turn → <strong>queue</strong>.",
            "Contacts looked up by name → <strong>hash table (dict)</strong>.",
            "File system folders → <strong>tree</strong>.",
            "Friends and maps → <strong>graph</strong>.",
        ]),
    ],
    "recap": [
        "A data structure is a way of organising data so certain operations are fast.",
        "No structure wins everywhere; choose by the operations you need most.",
        "Sets and dicts make lookups fast; lists keep order; stacks and queues control processing order.",
    ],
}

EXTRA["ds-arrays"] = {
    "intro": [
        ("h2", "The simplest structure: numbered slots"),
        ("p", "An array is a row of equal-sized boxes stored side by side in memory, each with a number starting at 0. Because the boxes are neighbours and the same size, the computer can jump to box 500 by simple arithmetic (start address plus 500 times the box size) without visiting boxes 0 to 499. That is why reading <code>arr[i]</code> is instant, no matter how big the array is."),
    ],
    "more": [
        ("h2", "What is cheap and what is costly"),
        *py('nums = [10, 20, 30, 40, 50]\n\nprint(nums[3])        # read by index: instant\nnums.append(60)       # add at the end: cheap\nnums.insert(0, 5)     # add at the front: every item must shift right\nprint(nums)\nnums.pop(0)           # remove from the front: every item shifts left\nprint(nums)'),
        ("p", "Adding at the <em>end</em> is cheap because nothing has to move. Adding or removing at the <em>front</em> is costly because every other item shifts one place, which is <code>O(n)</code> work. Remember this whenever you use a list as a queue."),
        ("h2", "Worked example: reverse in place"),
        ("p", "Two markers, one at each end, swap and move inward. No extra list is needed."),
        *py('def reverse(items):\n    left, right = 0, len(items) - 1\n    while left < right:\n        items[left], items[right] = items[right], items[left]\n        left += 1\n        right -= 1\n\ndata = [1, 2, 3, 4, 5]\nreverse(data)\nprint(data)'),
        ("h2", "Worked example: running maximum"),
        *py('temps = [18, 21, 19, 25, 23, 30, 28]\nbest = temps[0]\nfor t in temps[1:]:\n    if t > best:\n        best = t\nprint("highest:", best)'),
        ("h2", "Common array mistakes"),
        ("ul", [
            "Off-by-one: valid indexes are <code>0</code> to <code>len - 1</code>.",
            "Modifying a list while looping over it, which skips items. Loop over a copy or build a new list.",
            "Assuming an empty list has a first item; check <code>if items:</code> first.",
        ]),
    ],
    "recap": [
        "Arrays give instant access by index because items sit side by side in memory.",
        "Appending at the end is cheap; inserting or removing at the front shifts everything.",
        "Two-pointer techniques process an array in one pass without extra memory.",
    ],
}

EXTRA["ds-linked-lists"] = {
    "intro": [
        ("h2", "A treasure hunt of clues"),
        ("p", "In a linked list each item (a <em>node</em>) holds its value and a note saying where the next node is. To find the fifth item you must follow four notes from the start, like a treasure hunt where each clue points to the next. Unlike an array, the nodes can be scattered anywhere in memory. The trade-off: reaching item <em>k</em> is slow, but inserting or removing next to a node you already hold takes a moment because you only rewrite a couple of pointers."),
    ],
    "more": [
        ("h2", "Building and walking a list"),
        *py('class Node:\n    def __init__(self, value):\n        self.value = value\n        self.next = None\n\nhead = Node("A")\nhead.next = Node("B")\nhead.next.next = Node("C")\n\ncurrent = head\nwhile current:\n    print(current.value, end=" -> ")\n    current = current.next\nprint("None")'),
        ("h2", "Inserting after a node is just two pointer changes"),
        *py('class Node:\n    def __init__(self, value, next=None):\n        self.value = value\n        self.next = next\n\ndef to_list(head):\n    out = []\n    while head:\n        out.append(head.value)\n        head = head.next\n    return out\n\nhead = Node(1, Node(2, Node(4)))\nprint(to_list(head))\n\ntwo = head.next\ntwo.next = Node(3, two.next)      # new node points at 4, node 2 points at new node\nprint(to_list(head))'),
        ("h2", "Worked example: reverse a linked list"),
        ("p", "This is the most famous linked-list exercise. Walk the list once and flip each pointer to face backwards, keeping track of the previous node."),
        *py('class Node:\n    def __init__(self, value, next=None):\n        self.value = value\n        self.next = next\n\ndef to_list(head):\n    out = []\n    while head:\n        out.append(head.value)\n        head = head.next\n    return out\n\ndef reverse(head):\n    prev = None\n    while head:\n        nxt = head.next      # remember the rest\n        head.next = prev     # flip the pointer\n        prev = head          # move prev forward\n        head = nxt           # move on\n    return prev\n\nhead = Node(1, Node(2, Node(3, Node(4))))\nprint(to_list(reverse(head)))'),
        ("p", "Draw the four nodes on paper and follow the loop step by step. Watching the arrows flip is the fastest way to make this click."),
    ],
    "recap": [
        "A linked list is nodes chained by pointers; no index jumping, so lookup is <code>O(n)</code>.",
        "Insert or delete next to a known node is <code>O(1)</code>: just rewire pointers.",
        "Most linked-list problems are solved by careful pointer bookkeeping and one or two extra variables.",
    ],
}

EXTRA["ds-stacks-queues"] = {
    "intro": [
        ("h2", "Two ways of waiting in line"),
        ("p", "A <strong>stack</strong> is a pile of plates: you add to the top and take from the top, so the last one in is the first one out (LIFO). A <strong>queue</strong> is a line at a shop: people join at the back and leave from the front, so first in, first out (FIFO). Both restrict how you touch the data, and that restriction is exactly what makes them useful for modelling real processes."),
    ],
    "more": [
        ("h2", "A stack in action: undo"),
        *py('history = []\n\nfor action in ["type A", "type B", "delete B", "type C"]:\n    history.append(action)\n\nprint("undo ->", history.pop())\nprint("undo ->", history.pop())\nprint("remaining:", history)'),
        ("h2", "A queue in action: first come, first served"),
        ("p", "Use <code>collections.deque</code> for queues. Removing from the front of a plain list is slow because every item shifts, while <code>deque.popleft()</code> is instant."),
        *py('from collections import deque\n\nline = deque()\nline.append("Ada")\nline.append("Linus")\nline.append("Grace")\n\nprint("serving", line.popleft())\nprint("serving", line.popleft())\nprint("waiting:", list(line))'),
        ("h2", "Worked example: balanced brackets, explained"),
        ("p", "Each opening bracket is pushed; each closing bracket must match the most recent unclosed opener, which is exactly the top of the stack."),
        *py('def balanced(text):\n    pairs = {")": "(", "]": "[", "}": "{"}\n    stack = []\n    for ch in text:\n        if ch in "([{":\n            stack.append(ch)\n        elif ch in pairs:\n            if not stack or stack.pop() != pairs[ch]:\n                return False\n    return not stack\n\nfor s in ["([]{})", "([)]", "((", ""]:\n    print(repr(s), balanced(s))'),
        ("h2", "Where you meet these every day"),
        ("ul", [
            "The <strong>call stack</strong>: every function call is pushed, every return pops (this is why infinite recursion crashes with a \"stack overflow\").",
            "Browser <strong>back</strong> button and editor <strong>undo</strong>: stacks.",
            "Print spoolers, message brokers, task workers: queues.",
        ]),
    ],
    "recap": [
        "Stack = LIFO (push and pop at the top); queue = FIFO (enqueue at the back, dequeue at the front).",
        "Use a list for a stack and <code>collections.deque</code> for a queue.",
        "Matching-pairs problems (brackets, tags) are a natural fit for a stack.",
    ],
}

EXTRA["ds-trees"] = {
    "intro": [
        ("h2", "Data that branches"),
        ("p", "Lists and arrays are lines. Many things in the real world are not lines: a folder contains folders that contain files, an organisation chart branches from a CEO, a web page's HTML nests elements inside elements. A <strong>tree</strong> models this. It has one <em>root</em> at the top, each node can have <em>children</em>, and there are no loops. Trees appear everywhere: file systems, the DOM, databases, compilers and search."),
    ],
    "more": [
        ("h2", "Building a small tree and walking it"),
        *py('class Node:\n    def __init__(self, value):\n        self.value = value\n        self.children = []\n\nroot = Node("projects")\nsite = Node("site"); notes = Node("notes")\nroot.children += [site, notes]\nsite.children += [Node("index.html"), Node("style.css")]\nnotes.children.append(Node("todo.txt"))\n\ndef show(node, depth=0):\n    print("  " * depth + node.value)\n    for child in node.children:\n        show(child, depth + 1)\n\nshow(root)'),
        ("p", "Notice the function calls itself on each child. Trees and recursion are natural partners: a tree is either empty or a node with smaller trees beneath it."),
        ("h2", "Binary search tree: sorted and fast to search"),
        ("p", "In a binary search tree, everything in a node's left subtree is smaller and everything in its right subtree is larger. Searching therefore discards half of the remaining tree at every step, exactly like binary search on a sorted list."),
        *py('class BST:\n    def __init__(self, value):\n        self.value, self.left, self.right = value, None, None\n\n    def insert(self, v):\n        if v < self.value:\n            if self.left: self.left.insert(v)\n            else: self.left = BST(v)\n        else:\n            if self.right: self.right.insert(v)\n            else: self.right = BST(v)\n\n    def contains(self, v):\n        if v == self.value: return True\n        side = self.left if v < self.value else self.right\n        return bool(side) and side.contains(v)\n\n    def in_order(self):\n        return (self.left.in_order() if self.left else []) + [self.value] + (self.right.in_order() if self.right else [])\n\nt = BST(8)\nfor n in [3, 10, 1, 6, 14, 4]:\n    t.insert(n)\n\nprint(t.in_order())\nprint(t.contains(6), t.contains(7))'),
        ("p", "An <em>in-order</em> walk of a binary search tree visits values in sorted order, which is a neat way to see that the structure is doing its job."),
        ("h2", "Height decides speed"),
        ("p", "Search cost is proportional to the tree's <em>height</em>. A balanced tree with a million nodes is only about 20 levels tall. A degenerate tree (inserting already-sorted numbers) becomes a long chain of height a million, no better than a linked list. Real databases use self-balancing trees to guarantee good height."),
    ],
    "recap": [
        "A tree has a root, parent-child links and no cycles; it models hierarchies.",
        "Recursion is the natural way to process trees.",
        "In a binary search tree, left is smaller and right is larger, giving <code>O(log n)</code> search when balanced.",
        "In-order traversal of a BST yields sorted values.",
    ],
}

EXTRA["ds-hash-tables"] = {
    "intro": [
        ("h2", "The trick behind instant lookup"),
        ("p", "Searching a list means checking items one by one. A <strong>hash table</strong> avoids searching by <em>computing</em> where an item lives. It runs the key through a <em>hash function</em> that turns it into a number, and uses that number as a position in an array. To find the key later, hash it again and go straight to the same spot. Python's <code>dict</code> and <code>set</code> are hash tables, which is why they are so fast."),
    ],
    "more": [
        ("h2", "Watching hashing happen"),
        *py('buckets = 8\nfor key in ["ada", "linus", "grace", "alan"]:\n    slot = sum(ord(c) for c in key) % buckets   # a toy hash function\n    print(f"{key:<6} -> slot {slot}")'),
        ("p", "Each key maps to a slot number. Two different keys can land on the same slot; that is called a <strong>collision</strong>, and real tables handle it by keeping a small list per slot or probing to the next free slot. With a good hash function and enough slots collisions are rare and lookups stay near <code>O(1)</code>."),
        ("h2", "What can be a key?"),
        ("p", "Keys must be <em>hashable</em>, meaning immutable. Strings, numbers and tuples work. Lists and dicts do not, because their contents (and therefore their hash) could change."),
        *py('locations = {(0, 0): "start", (2, 5): "shop"}\nprint(locations[(2, 5)])\n\ntry:\n    bad = {[1, 2]: "nope"}\nexcept TypeError as e:\n    print("TypeError:", e)'),
        ("h2", "Worked example: find duplicates in one pass"),
        *py('def first_duplicate(items):\n    seen = set()\n    for x in items:\n        if x in seen:\n            return x\n        seen.add(x)\n    return None\n\nprint(first_duplicate([3, 1, 4, 1, 5, 9]))\nprint(first_duplicate([1, 2, 3]))'),
        ("p", "Without a set you would compare every pair of items, which is <code>O(n^2)</code>. With one you touch each item once: <code>O(n)</code>. Turning a nested loop into a set lookup is one of the most valuable optimisations you will ever learn."),
    ],
    "recap": [
        "A hash table computes a slot from the key, giving average <code>O(1)</code> lookup, insert and delete.",
        "Collisions are handled internally; you just use <code>dict</code> and <code>set</code>.",
        "Keys must be immutable (hashable): use tuples, not lists.",
        "A <code>set</code> or <code>dict</code> often replaces a slow nested loop.",
    ],
}

EXTRA["ds-graphs"] = {
    "intro": [
        ("h2", "Anything connected is a graph"),
        ("p", "A graph is just <em>things</em> (nodes, or vertices) and <em>connections</em> between them (edges). Friends on a social network, cities joined by roads, web pages linking to each other, tasks that depend on other tasks: all graphs. Trees are a special, well-behaved kind of graph. Graph algorithms answer questions such as \"is there a route from A to B?\", \"what is the shortest route?\" and \"who are the friends of friends?\""),
    ],
    "more": [
        ("h2", "Store a graph as an adjacency list"),
        ("p", "The most common representation is a dictionary that maps each node to the list of its neighbours."),
        *py('graph = {\n    "Ada":   ["Linus", "Grace"],\n    "Linus": ["Ada", "Alan"],\n    "Grace": ["Ada", "Alan"],\n    "Alan":  ["Linus", "Grace", "Tim"],\n    "Tim":   ["Alan"],\n}\n\nprint(graph["Alan"])\nprint(len(graph["Ada"]), "friends")'),
        ("h2", "Breadth-first search finds the shortest path"),
        ("p", "BFS explores all neighbours first, then their neighbours, spreading outward one layer at a time like ripples in a pond. Because it visits nearer nodes before farther ones, the first time it reaches a target it has found the route with the fewest hops."),
        *py('from collections import deque\n\ngraph = {\n    "Ada": ["Linus", "Grace"], "Linus": ["Ada", "Alan"],\n    "Grace": ["Ada", "Alan"], "Alan": ["Linus", "Grace", "Tim"], "Tim": ["Alan"],\n}\n\ndef shortest_path(start, goal):\n    queue = deque([[start]])\n    seen = {start}\n    while queue:\n        path = queue.popleft()\n        node = path[-1]\n        if node == goal:\n            return path\n        for nxt in graph[node]:\n            if nxt not in seen:\n                seen.add(nxt)\n                queue.append(path + [nxt])\n    return None\n\nprint(shortest_path("Ada", "Tim"))'),
        ("h2", "Why the seen set is essential"),
        ("p", "Graphs can contain loops (Ada knows Linus, Linus knows Ada). Without remembering visited nodes, the search would walk in circles forever. Marking nodes as seen the moment you queue them keeps every node visited at most once."),
        ("h2", "Depth-first search explores one branch fully"),
        *py('graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}\n\ndef dfs(node, seen=None):\n    seen = seen if seen is not None else []\n    seen.append(node)\n    for nxt in graph[node]:\n        if nxt not in seen:\n            dfs(nxt, seen)\n    return seen\n\nprint(dfs("A"))'),
    ],
    "recap": [
        "A graph is nodes plus edges; store it as a dict of neighbour lists.",
        "BFS uses a queue and finds shortest paths in unweighted graphs; DFS uses recursion (or a stack) and explores deeply.",
        "Always track visited nodes to avoid infinite loops.",
    ],
}

EXTRA["ds-big-o"] = {
    "intro": [
        ("h2", "The question Big O answers"),
        ("p", "Two programs give the same answer; which is better? Timing them on your laptop is unreliable, because it depends on the machine and the sample data. <strong>Big O notation</strong> instead describes how the work <em>grows as the input grows</em>. If the input doubles, does the work stay the same, double, or quadruple? That growth rate is what decides whether a program still works with a million users."),
        ("p", "Big O ignores small details (a constant factor of 2, a lower-order term) and focuses on the shape of the growth."),
    ],
    "more": [
        ("h2", "Feel the growth"),
        ("p", "Count the operations each style of algorithm does for an input of size n. The numbers, not the notation, are what to remember."),
        *py('import math\n\nprint(f"{\'n\':>8} {\'O(log n)\':>10} {\'O(n)\':>10} {\'O(n log n)\':>12} {\'O(n^2)\':>16}")\nfor n in [10, 1_000, 1_000_000]:\n    print(f"{n:>8} {math.log2(n):>10.0f} {n:>10} {n * math.log2(n):>12.0f} {n * n:>16}")'),
        ("p", "At n = 1,000,000 a logarithmic algorithm does about 20 steps, a linear one a million, and a quadratic one <em>a trillion</em>. That is the difference between instant and never finishing."),
        ("h2", "Reading Big O straight from code"),
        *py('def constant(items):            # O(1): one step regardless of size\n    return items[0]\n\ndef linear(items):              # O(n): one pass\n    total = 0\n    for x in items:\n        total += x\n    return total\n\ndef quadratic(items):           # O(n^2): loop inside a loop\n    pairs = 0\n    for a in items:\n        for b in items:\n            pairs += 1\n    return pairs\n\ndata = list(range(100))\nprint(constant(data), linear(data), quadratic(data))'),
        ("ul", [
            "No loop over the input → <code>O(1)</code>.",
            "One loop over the input → <code>O(n)</code>.",
            "A loop nested inside a loop over the same input → <code>O(n^2)</code>.",
            "Halving the problem each step (binary search) → <code>O(log n)</code>.",
            "Two loops one after the other (not nested) → still <code>O(n)</code>; add, then drop constants.",
        ]),
        ("h2", "Trade time for memory"),
        ("p", "Faster is often possible if you spend memory. Checking for duplicates with nested loops is <code>O(n^2)</code> time and <code>O(1)</code> extra space; using a set is <code>O(n)</code> time and <code>O(n)</code> space. Most real optimisations are exactly this swap."),
    ],
    "recap": [
        "Big O describes how work grows with input size, ignoring constants.",
        "Order to remember: <code>O(1)</code> &lt; <code>O(log n)</code> &lt; <code>O(n)</code> &lt; <code>O(n log n)</code> &lt; <code>O(n^2)</code>.",
        "Count loops: one is linear, nested is quadratic, halving is logarithmic.",
        "Extra memory (a set or dict) frequently buys a big speedup.",
    ],
}

EXTRA["algo-searching"] = {
    "intro": [
        ("h2", "Finding a needle, faster"),
        ("p", "Searching is the most common job in computing. If you have no order to exploit you must check items one by one. If the data is sorted you can do far better by using the order, the way you open a dictionary near the middle rather than at page one. The idea behind <strong>binary search</strong> is to throw away half of the remaining possibilities with every question."),
    ],
    "more": [
        ("h2", "How many guesses to find a number from 1 to 1,000?"),
        ("p", "Guess the middle (500). Told \"higher\", the answer is now in 501-1000, half the size. Repeat. You need at most 10 guesses because 2 to the power 10 is 1,024. That is <code>O(log n)</code>."),
        *py('def binary_search(sorted_items, target):\n    lo, hi = 0, len(sorted_items) - 1\n    steps = 0\n    while lo <= hi:\n        steps += 1\n        mid = (lo + hi) // 2\n        if sorted_items[mid] == target:\n            return mid, steps\n        if sorted_items[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1, steps\n\nnumbers = list(range(1, 1001))\nprint(binary_search(numbers, 777))\nprint(binary_search(numbers, 5000))'),
        ("p", "It found 777 in at most 10 steps out of 1,000 items. The same code finds an item among a billion in about 30 steps."),
        ("h2", "The three things that go wrong"),
        ("ul", [
            "<strong>The data must be sorted</strong>. On unsorted data binary search silently returns wrong answers.",
            "<strong>Off-by-one on the boundaries</strong>: use <code>lo &lt;= hi</code> and move to <code>mid + 1</code> / <code>mid - 1</code>.",
            "<strong>Infinite loops</strong>: if you set <code>lo = mid</code> instead of <code>mid + 1</code>, the range may never shrink.",
        ]),
        ("h2", "Use the library when you can"),
        *py('from bisect import bisect_left\n\nprices = [10, 20, 20, 30, 45]\nprint(bisect_left(prices, 20))    # first position where 20 fits\nprint(bisect_left(prices, 25))    # where 25 would be inserted'),
    ],
    "recap": [
        "Linear search checks each item: <code>O(n)</code>, works on any data.",
        "Binary search halves the range each step: <code>O(log n)</code>, needs sorted data.",
        "Be careful with boundaries; prefer <code>bisect</code> in real code.",
    ],
}

EXTRA["algo-sorting"] = {
    "intro": [
        ("h2", "Why sorting matters"),
        ("p", "Sorted data unlocks fast searching, easy duplicate detection, simple merging and readable reports. Sorting is also the classic place to study algorithm design, because there are many correct ways, with very different costs. In everyday Python you will simply call <code>sorted()</code>, but understanding how sorts work teaches you to think about efficiency."),
    ],
    "more": [
        ("h2", "Bubble sort: the intuitive one"),
        ("p", "Repeatedly walk the list and swap neighbours that are out of order. Big values \"bubble\" to the end. It is simple but takes <code>O(n^2)</code> comparisons, so it is only for teaching."),
        *py('def bubble_sort(items):\n    items = items[:]\n    for end in range(len(items) - 1, 0, -1):\n        for i in range(end):\n            if items[i] > items[i + 1]:\n                items[i], items[i + 1] = items[i + 1], items[i]\n    return items\n\nprint(bubble_sort([5, 2, 9, 1, 7]))'),
        ("h2", "Merge sort: divide and conquer"),
        ("p", "Split the list in half, sort each half (recursively), then <em>merge</em> two sorted halves by repeatedly taking the smaller front item. It is <code>O(n log n)</code>, dramatically faster on big inputs."),
        *py('def merge_sort(items):\n    if len(items) <= 1:\n        return items\n    mid = len(items) // 2\n    left, right = merge_sort(items[:mid]), merge_sort(items[mid:])\n\n    merged, i, j = [], 0, 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            merged.append(left[i]); i += 1\n        else:\n            merged.append(right[j]); j += 1\n    return merged + left[i:] + right[j:]\n\nprint(merge_sort([5, 2, 9, 1, 7, 3]))'),
        ("h2", "Sorting by more than one field"),
        *py('people = [("Ann", 31), ("Bob", 25), ("Cy", 31)]\nby_age_then_name = sorted(people, key=lambda p: (-p[1], p[0]))\nprint(by_age_then_name)'),
        ("p", "In real code, call <code>sorted()</code> or <code>list.sort()</code>. Python's built-in <em>Timsort</em> is stable, fast and already tuned. Reach for hand-written sorts only for learning or very special cases."),
    ],
    "recap": [
        "Simple sorts (bubble, insertion) are <code>O(n^2)</code>; merge and quick sort are <code>O(n log n)</code>.",
        "Merge sort divides, sorts halves recursively, then merges.",
        "Use built-in <code>sorted</code> with a <code>key</code> for real work; it is stable.",
    ],
}

EXTRA["algo-recursion"] = {
    "intro": [
        ("h2", "Solving a problem by shrinking it"),
        ("p", "Recursion means a function that calls <em>itself</em> on a smaller version of the same problem. Russian nesting dolls are a good picture: to count the dolls, open the outer one, count what is inside, add one. Every recursive solution needs two parts: a <strong>base case</strong> (the smallest problem, answered directly) and a <strong>recursive case</strong> (reduce the problem and trust the function to solve the smaller one). Forget the base case and the function never stops."),
    ],
    "more": [
        ("h2", "Factorial, traced"),
        *py('def factorial(n):\n    if n <= 1:                  # base case\n        return 1\n    return n * factorial(n - 1) # recursive case\n\nprint(factorial(5))'),
        ("p", "Trace it: <code>factorial(3)</code> waits for <code>factorial(2)</code>, which waits for <code>factorial(1)</code>. That returns 1, then 2 * 1 = 2, then 3 * 2 = 6. Each call waits on the <strong>call stack</strong> until the one below finishes."),
        ("h2", "Watch the calls happen"),
        *py('def countdown(n, depth=0):\n    print("  " * depth + f"countdown({n})")\n    if n == 0:\n        print("  " * depth + "liftoff")\n        return\n    countdown(n - 1, depth + 1)\n    print("  " * depth + f"back in countdown({n})")\n\ncountdown(2)'),
        ("h2", "Worked example: summing a nested list"),
        *py('def total(node):\n    if isinstance(node, int):\n        return node\n    return sum(total(child) for child in node)\n\nprint(total([1, [2, 3], [4, [5, 6]]]))'),
        ("h2", "Making Fibonacci fast with memoization"),
        ("p", "The obvious version recomputes the same values over and over, taking exponential time. Remembering answers (memoization) turns it linear."),
        *py('from functools import lru_cache\n\ncalls = 0\n\ndef slow(n):\n    global calls\n    calls += 1\n    return n if n < 2 else slow(n - 1) + slow(n - 2)\n\n@lru_cache(None)\ndef fast(n):\n    return n if n < 2 else fast(n - 1) + fast(n - 2)\n\nprint(slow(20), "calls:", calls)\nprint(fast(20), "cache size:", fast.cache_info().currsize)'),
    ],
    "recap": [
        "Every recursive function needs a base case and a step that moves toward it.",
        "Calls stack up and unwind; a missing base case causes a stack overflow.",
        "Recursion suits nested and tree-shaped data; memoize when subproblems repeat.",
    ],
}

EXTRA["algo-greedy"] = {
    "intro": [
        ("h2", "Always take the best-looking option right now"),
        ("p", "A greedy algorithm builds a solution one step at a time, and at each step picks whatever looks best <em>at that moment</em>, never reconsidering. When it works, greedy is wonderfully simple and fast. When it does not, it gives confident wrong answers, so the real skill is knowing when it is safe. Making change with coins is the standard example."),
    ],
    "more": [
        ("h2", "Making change: greedy works here"),
        *py('def make_change(amount, coins=(25, 10, 5, 1)):\n    used = []\n    for coin in coins:              # largest first\n        while amount >= coin:\n            amount -= coin\n            used.append(coin)\n    return used\n\nprint(make_change(63))'),
        ("h2", "...and greedy fails here"),
        ("p", "With coins 1, 3 and 4, making 6 greedily takes 4 + 1 + 1 (three coins), but the best answer is 3 + 3 (two coins). Greedy is only correct when the coin system has a special structure. This is why you must be able to <em>justify</em> a greedy choice, not just hope."),
        *py('def greedy(amount, coins):\n    used = []\n    for c in sorted(coins, reverse=True):\n        while amount >= c:\n            amount -= c\n            used.append(c)\n    return used\n\nprint(greedy(6, [1, 3, 4]))     # greedy: 3 coins\nprint([3, 3])                   # optimal: 2 coins'),
        ("h2", "Interval scheduling: a greedy that is provably correct"),
        ("p", "To fit the most meetings in one room, always pick the meeting that <em>ends earliest</em>. It leaves the most room for the rest, and this can be proven optimal."),
        *py('meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]\nchosen, last_end = [], 0\nfor start, end in sorted(meetings, key=lambda m: m[1]):\n    if start >= last_end:\n        chosen.append((start, end))\n        last_end = end\nprint(chosen)'),
    ],
    "recap": [
        "Greedy picks the locally best choice each step and never looks back.",
        "It is fast and simple but only correct for problems with the right structure.",
        "Sort first, then sweep; and always try to find a counterexample before trusting a greedy rule.",
    ],
}

EXTRA["algo-backtracking"] = {
    "intro": [
        ("h2", "Try, and undo if it does not work"),
        ("p", "Backtracking is how you would solve a maze: walk down a path; if you hit a dead end, step back to the last junction and try another turn. In code it means building a solution one choice at a time, exploring where it leads, and <em>undoing</em> the choice to try the next option. It systematically explores all possibilities while abandoning hopeless branches early. Puzzles such as Sudoku, N-Queens, generating subsets and permutations are all solved this way."),
        ("p", "Every backtracking solution follows the same three-beat rhythm: <strong>choose</strong> an option, <strong>explore</strong> further with it, <strong>unchoose</strong> it."),
    ],
    "more": [
        ("h2", "Generating every subset"),
        *py('def subsets(items):\n    result, current = [], []\n\n    def explore(start):\n        result.append(current[:])          # record what we have so far\n        for i in range(start, len(items)):\n            current.append(items[i])       # choose\n            explore(i + 1)                 # explore\n            current.pop()                  # unchoose\n\n    explore(0)\n    return result\n\nprint(subsets([1, 2, 3]))'),
        ("h2", "Generating permutations"),
        *py('def permutations(items):\n    result, current, used = [], [], [False] * len(items)\n\n    def explore():\n        if len(current) == len(items):\n            result.append(current[:])\n            return\n        for i, x in enumerate(items):\n            if used[i]:\n                continue\n            used[i] = True; current.append(x)      # choose\n            explore()                              # explore\n            current.pop(); used[i] = False         # unchoose\n\n    explore()\n    return result\n\nprint(permutations(["A", "B", "C"]))'),
        ("h2", "Pruning: stop bad branches early"),
        ("p", "Backtracking checks constraints as it goes and abandons a branch the instant it cannot succeed. Here we find combinations that add up to a target, cutting off any branch that already exceeds it."),
        *py('def combos(nums, target):\n    nums.sort()\n    out, cur = [], []\n\n    def go(start, remaining):\n        if remaining == 0:\n            out.append(cur[:]); return\n        for i in range(start, len(nums)):\n            if nums[i] > remaining:\n                break                        # prune: too big, and all later ones are bigger\n            cur.append(nums[i])\n            go(i, remaining - nums[i])           # can reuse the same number\n            cur.pop()\n\n    go(0, target)\n    return out\n\nprint(combos([2, 3, 6, 7], 7))'),
    ],
    "recap": [
        "Backtracking = choose, explore, unchoose; it tries every possibility systematically.",
        "Copy the current path when saving a result (<code>current[:]</code>).",
        "Prune branches as early as possible; otherwise the cost explodes exponentially.",
    ],
}

EXTRA["algo-dynamic-programming"] = {
    "intro": [
        ("h2", "Do not solve the same problem twice"),
        ("p", "If a friend asks you the same difficult question ten times, you would write the answer down after the first time. <strong>Dynamic programming</strong> (DP) applies that idea to algorithms. When a problem breaks into smaller subproblems that <em>repeat</em>, you solve each subproblem once, store the result, and reuse it. Problems that took exponential time recursively often become fast and polynomial."),
        ("p", "Two signs that DP may help: the problem asks for a best/count/yes-no answer, and a naive recursion keeps recomputing the same inputs."),
    ],
    "more": [
        ("h2", "From slow recursion to DP, in three steps"),
        ("p", "Count ways to climb n stairs taking 1 or 2 steps at a time. First the plain recursion, then the same idea with a memo, then a bottom-up table."),
        *py('from functools import lru_cache\n\ndef ways_slow(n):\n    return 1 if n <= 1 else ways_slow(n - 1) + ways_slow(n - 2)\n\n@lru_cache(None)\ndef ways_memo(n):\n    return 1 if n <= 1 else ways_memo(n - 1) + ways_memo(n - 2)\n\ndef ways_table(n):\n    dp = [1, 1] + [0] * (n - 1)\n    for i in range(2, n + 1):\n        dp[i] = dp[i - 1] + dp[i - 2]\n    return dp[n]\n\nprint(ways_slow(15), ways_memo(15), ways_table(15))\nprint(ways_table(50))'),
        ("h2", "The DP recipe"),
        ("ul", [
            "<strong>State</strong>: what does <code>dp[i]</code> mean, in one sentence?",
            "<strong>Transition</strong>: how does <code>dp[i]</code> follow from smaller states?",
            "<strong>Base cases</strong>: which values are known directly?",
            "<strong>Order</strong>: fill the table so dependencies are ready first.",
            "<strong>Answer</strong>: which cell holds the result?",
        ]),
        ("h2", "Coin change, where greedy failed"),
        ("p", "DP solves the coin problem that greedy got wrong. <code>dp[a]</code> is the fewest coins needed to make amount <code>a</code>."),
        *py('def fewest_coins(coins, amount):\n    INF = float("inf")\n    dp = [0] + [INF] * amount\n    for a in range(1, amount + 1):\n        for c in coins:\n            if c <= a and dp[a - c] + 1 < dp[a]:\n                dp[a] = dp[a - c] + 1\n    return dp[amount] if dp[amount] != INF else -1\n\nprint(fewest_coins([1, 3, 4], 6))      # 2  (3 + 3)\nprint(fewest_coins([2], 3))            # -1 (impossible)'),
        ("p", "For 6 with coins 1, 3, 4 greedy needed three coins; DP correctly finds two. DP considers <em>every</em> option for each amount, remembering the best."),
    ],
    "recap": [
        "DP stores answers to overlapping subproblems so each is solved once.",
        "Define the state, the transition and the base cases, then fill a table (or memoize).",
        "DP finds optimal answers where greedy can fail, at the cost of extra memory.",
    ],
}
