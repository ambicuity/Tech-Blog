---
layout: page
title: "71. Simplify Path"
permalink: /courses/leetcode/prob-71-simplify-path/
---

# 71. Simplify Path

## 1. The Question
Given a string `path`, which is an **absolute path** (starting with a slash `'/'`) to a file or directory in a Unix-style file system, convert it to the simplified **canonical path**.

In a Unix-style file system, a period `'.'` refers to the current directory, a double period `'..'` refers to the directory up a level, and any multiple consecutive slashes (i.e. `'//'`) are treated as a single slash `'/'`. For this problem, any other format of periods such as `'...'` are treated as file/directory names.

The canonical path should have the following format:
1.  The path starts with a single slash `'/'`.
2.  Any two directories are separated by a single slash `'/'`.
3.  The path does not end with a trailing `'/'`.
4.  The path only contains the directories on the path from the root directory to the target file or directory (i.e., no period `'.'` or double period `'..'`).

Return the simplified canonical path.

### Example 1
**Input**: `path = "/home/"`
**Output**: `"/home"`

### Example 2
**Input**: `path = "/../"`
**Output**: `"/"`
**Explanation**: Going one level up from the root directory is a no-op, as the root level is the highest level you can go.

### Example 3
**Input**: `path = "/home//foo/"`
**Output**: `"/home/foo"`

---

## 2. Explanation
We need to parse the path components and simulate directory navigation.
Split the string by `/`.
-   `""` (empty string from `//`): Ignore.
-   `"."`: Ignore (current dir).
-   `".."`: Go up. Pop from stack (if stack not empty).
-   `"name"`: Go down. Push to stack.

Finally, join the stack with `/`.

-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

---

## 3. Pseudo Code
```text
components = path.split('/')
stack = []

For comp in components:
    if comp == "" or comp == ".":
        continue
    if comp == "..":
        if stack: stack.pop()
    else:
        stack.append(comp)

Return "/" + stack.join("/")
```

---

## 4. Optimal Code (Python)

```python
class Solution:
    def simplifyPath(self, path: str) -> str:
        # Split by slash. This handles multiple slashes automatically 
        # as they produce empty strings.
        components = path.split("/")
        stack = []
        
        for comp in components:
            if comp == "" or comp == ".":
                continue
            elif comp == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(comp)
                
        return "/" + "/".join(stack)
```

---

## 5. Complexity
-   **Time**: $O(N)$.
-   **Space**: $O(N)$.

## 6. Example Walkthrough
`path = "/a/./b/../../c/"`

1.  Split: `["", "a", ".", "b", "..", "..", "c", ""]`.
2.  `""`: Skip.
3.  `"a"`: Push. Stack: `["a"]`.
4.  `"."`: Skip.
5.  `"b"`: Push. Stack: `["a", "b"]`.
6.  `".."`: Pop `b`. Stack: `["a"]`.
7.  `".."`: Pop `a`. Stack: `[]`.
8.  `"c"`: Push. Stack: `["c"]`.
9.  `""`: Skip.

Join: `/c`.
