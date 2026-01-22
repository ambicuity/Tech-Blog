---
layout: page
title: "AI Ch.3: Solving Problems by Search"
permalink: /courses/ai/ch3-search/
---

# Chapter 3: Solving Problems by Searching

> **Reference**: *Artificial Intelligence: A Modern Approach* by Russell & Norvig, Chapter 3

In many AI problems, the sequence of steps required to reach a goal is not known in advance. The agent must **search** through the state space to find a solution.

## 3.1 Problem Formulation

To define a search problem effectively, we need five components:

1.  **Initial State** ($S_0$): Where the agent starts.
2.  **Actions** ($A(s)$): A description of possible actions available in a given state.
3.  **Transition Model** ($Result(s, a)$): Returns the state that results from doing action $a$ in state $s$.
4.  **Goal Test**: Determines whether a given state is a goal state.
5.  **Path Cost** ($g(n)$): Assigns a numeric cost to each path (e.g., distance, time, energy).

The solution is a sequence of actions (a plan) that transforms the initial state into a goal state.

---

## 3.2 Uninformed Search Strategies

Uninformed (blind) search strategies use only the information available in the problem definition. They do not know if one non-goal state is "better" than another.

### 1. Breadth-First Search (BFS)
Expands the shallowest nodes first. Implemented using a **FIFO Queue**.

-   **Complete**: Yes (if branching factor $b$ is finite).
-   **Optimal**: Yes (if path cost is non-decreasing function of depth).
-   **Time Complexity**: $O(b^d)$, where $d$ is depth of solution.
-   **Space Complexity**: $O(b^d)$. **(This is the main drawback)**.
    - *Example*: If $b=10$ and $d=12$, BFS needs Petabytes of RAM.

### 2. Depth-First Search (DFS)
Expands the deepest nodes first. Implemented using a **LIFO Stack** (or Recursion).

-   **Complete**: No (fails in infinite spaces or loops).
-   **Optimal**: No (can find a long path before a short one).
-   **Space Complexity**: $O(b \cdot m)$, where $m$ is max depth. **(Very Efficient)**.

### 3. Iterative Deepening Search (IDS)
Combines the benefits of BFS and DFS. Runs DFS with depth limit $L=0, 1, 2, \dots$.

-   **Complete**: Yes.
-   **Optimal**: Yes.
-   **Space**: $O(b \cdot d)$.
-   *Note*: The overhead of regenerating nodes is only about 11% for $b=10$.

---

## 3.3 Informed (Heuristic) Search

Informed methods use a **Heuristic Function $h(n)$**:
$$ h(n) = \text{estimated cost of the cheapest path from node } n \text{ to the goal.} $$

### Greedy Best-First Search
Expands the node that appears to be closest to the goal ($min(h(n))$).
-   **Pro**: Fast.
-   **Con**: Not optimal. Can get stuck in loops or dead ends.

### A* Search (The Gold Standard)
Expands node with minimum $f(n)$.
$$ f(n) = g(n) + h(n) $$
-   $g(n)$: Cost to reach node $n$ from start.
-   $h(n)$: Estimated cost to goal.

#### Conditions for Optimality
A* is **Optimal** if the heuristic $h(n)$ is **Admissible**.
> **Admissible**: $0 \le h(n) \le h^*(n)$. The heuristic never overestimates.
> (e.g., Straight-line distance is admissible for road travel).

#### Python Implementation of A*

```python
import heapq

class Node:
    def __init__(self, position, parent=None, g=0, h=0):
        self.position = position
        self.parent = parent
        self.g = g  # Cost from start
        self.h = h  # Heuristic to goal
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f

def astar(maze, start, end):
    # Open list: Priority Queue
    open_list = []
    heapq.heappush(open_list, Node(start, None, 0, 0))
    
    # Closed set: Visited nodes
    closed_set = set()

    while open_list:
        current_node = heapq.heappop(open_list)
        
        # Goal Reached
        if current_node.position == end:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1] # Return reversed path

        closed_set.add(current_node.position)

        # Generate Children (Neighbors)
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
            node_position = (current_node.position[0] + new_position[0], 
                           current_node.position[1] + new_position[1])

            # Check validity (walls, bounds)
            if not is_valid(maze, node_position) or node_position in closed_set:
                continue

            # Calculate costs
            g = current_node.g + 1
            h = ((node_position[0] - end[0]) ** 2) + ((node_position[1] - end[1]) ** 2) # Euclidean dist
            new_node = Node(node_position, current_node, g, h)

            # Add to open list (if not present with lower g)
            heapq.heappush(open_list, new_node)

    return None # No path found
```

## 3.4 Heuristics comparisons
The choice of heuristics matters.
For the **8-Puzzle**:
-   $h_1$: Number of misplaced tiles.
-   $h_2$: Sum of Manhattan distances of tiles from goal positions.

$h_2$ dominates $h_1$ ($h_2(n) \ge h_1(n)$ for all $n$). A* using $h_2$ will explore **fewer** nodes than A* using $h_1$.

## 3.5 Summary Table

| Algorithm | Complete? | Optimal? | Time Complexity | Space Complexity |
| :--- | :---: | :---: | :---: | :---: |
| **BFS** | Yes | Yes | $O(b^d)$ | $O(b^d)$ |
| **DFS** | No | No | $O(b^m)$ | $O(bm)$ |
| **IDS** | Yes | Yes | $O(b^d)$ | $O(bd)$ |
| **A\*** | Yes | Yes | Exp | Exp |
