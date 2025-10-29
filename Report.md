# Comparative Analysis of PageRank, Personalized PageRank, and Topic-Sensitive PageRank

This document explains three closely related algorithms:
1. Normal PageRank
2. Personalized PageRank
3. Topic-Sensitive PageRank

The explanation covers intuition, mathematical formulation, behavior, and use cases. All notation and equations are written directly in plain text.

---

## 1. Normal PageRank

### 1.1 Intuition
Normal PageRank estimates how "important" each node in a directed graph is (for example, each paper in a citation network). The basic model is a random surfer who moves from node to node by following outgoing links. Sometimes the surfer gets bored and jumps to a random node in the graph. The steady-state probability of being at each node is its PageRank score.

A node receives high rank if it is pointed to by other high-rank nodes. In citation terms, a paper is important if it is cited by other important papers.

### 1.2 Mathematical definition
Let:
- G be a directed graph.
- V be the set of nodes in G.
- N = number of nodes = |V|.
- d = damping factor, where 0 < d < 1 (typical value is 0.85).
- PR(i) = PageRank score of node i.
- Out(j) = number of outgoing edges from node j.

Then the PageRank score satisfies the fixed point equation:

PR(i) = d * sum over j in In(i) of ( PR(j) / Out(j) )  +  (1 - d) * (1 / N)

Where:
- In(i) is the set of nodes that have an edge to i (nodes that link to i).
- The first term is the probability mass arriving from in-neighbors following links.
- The second term is the teleportation term, which represents the chance that the surfer jumps uniformly to any node.

In vector form, if we write PR as an N x 1 vector and M as the column-normalized adjacency matrix (so M_ij = 1 / Out(j) if j links to i, else 0), then:

PR = d * M * PR + (1 - d) * u

where u is an N x 1 uniform vector where each entry is 1 / N.

This is solved iteratively until convergence.

### 1.3 Interpretation
- PR(i) is high if many important nodes point to i.
- Teleportation prevents getting stuck in dead ends (nodes with no outgoing edges) and spider traps (strongly connected subgraphs that only point to themselves).
- The ranking is global. It does not depend on any user, topic, or query.

### 1.4 Typical use
- Global influence ranking: "What are the most important papers overall in this filtered citation graph"
- Web search (classical Google PageRank idea)
- Detecting authoritative nodes in citation, social, or hyperlink graphs

---

## 2. Personalized PageRank

### 2.1 Intuition
Personalized PageRank modifies the behavior of the random surfer. The surfer still follows outgoing links with probability d, but when they teleport (with probability 1 - d), they do not jump uniformly to all nodes. Instead, they jump according to a chosen "preference distribution" over nodes.

This preference distribution reflects some bias. For example:
- A specific user's interests
- A chosen set of seed papers
- A specific author, institution, or entity of interest

As a result, Personalized PageRank measures importance "relative to what we care about", instead of importance in general.

### 2.2 Mathematical definition
We define a personalization vector p of length N, where:
- p(i) >= 0 for all nodes i
- sum over i of p(i) = 1
- p(i) is higher for nodes we care about more

Then Personalized PageRank is defined by:

PPR = d * M * PPR + (1 - d) * p

Compare this to the normal PageRank formula:

PR = d * M * PR + (1 - d) * u

The only difference is that u (which was uniform in normal PageRank) is now replaced by p (which is biased). The matrix M and damping d are the same type as before.

In scalar form for node i:

PPR(i) = d * sum over j in In(i) of ( PPR(j) / Out(j) )  +  (1 - d) * p(i)

Where p(i) is large only for nodes we want to emphasize.

### 2.3 Interpretation
- The algorithm ranks nodes by "how reachable they are from the preferred set".
- Nodes that are strongly connected to the preferred nodes through citation paths will get higher scores.
- Two different users or two different preference sets will, in general, get two different Personalized PageRank vectors.

### 2.4 Typical use
- Recommendation systems ("papers similar to what I already like")
- Query-focused ranking ("show me influence around this subset of nodes, not globally")
- Local authority detection ("who matters to this specific subcommunity")

### 2.5 Cost consideration
For a single preference vector p, computing Personalized PageRank is about as expensive as computing normal PageRank. But if you need a different PPR vector for every user, every session, or every query, then cost grows, because each preference vector p leads to a different output.

---

## 3. Topic-Sensitive PageRank

### 3.1 Intuition
Topic-Sensitive PageRank is a structured and reusable version of Personalized PageRank.

Instead of creating a personalization vector p for every user, we create one personalization vector for each topic of interest (for example "security", "hashing", "streaming", "timeseries", "search").

For a given topic t, we:
1. Identify a set of nodes relevant to that topic. In the assignment, a paper is considered relevant to a topic if its title contains the topic keyword.
2. Build a personalization vector p_t that places probability mass only on those topic-relevant nodes.
3. Run PageRank with teleport restricted to that topic vector.

This produces a PageRank vector specific to that topic. We can then rank all papers in the graph by their topic-sensitive score.

### 3.2 Mathematical definition
For each topic t, define a topic personalization vector p_t with:
- p_t(i) > 0 if node i is relevant to topic t
- p_t(i) = 0 otherwise
- sum over i of p_t(i) = 1

Then:

TSR_t = d * M * TSR_t + (1 - d) * p_t

Where:
- TSR_t is the Topic-Sensitive PageRank vector for topic t.
- M is again the same column-normalized link matrix.
- d is the same damping factor (for example d = 0.85).
- p_t controls where the random surfer teleports.

So mathematically, Topic-Sensitive PageRank is the same equation as Personalized PageRank, just with a specific way of constructing the personalization vector p_t (based on topic membership rather than user preference).

In scalar form, for node i, and topic t:

TSR_t(i) = d * sum over j in In(i) of ( TSR_t(j) / Out(j) )  +  (1 - d) * p_t(i)

### 3.3 Interpretation
- TSR_t(i) is high if node i is "authoritative within topic t".
- The algorithm favors nodes that are:
  - either directly marked as belonging to the topic, or
  - strongly cited by topic papers, or
  - part of citation structures that connect topic papers.
- This solves an important limitation of normal PageRank. Normal PageRank might rank a highly cited systems paper above a highly cited security paper, even if you only care about security. Topic-Sensitive PageRank fixes that by biasing teleportation toward the security-relevant papers only.

### 3.4 Typical use
- Academic literature analysis per topic (for example, "top 10 security papers in the subgraph").
- Topical authority discovery.
- Context-aware retrieval in search systems, using predefined domains rather than per-user preferences.

### 3.5 Why it is practical
Topic-Sensitive PageRank gives you a reusable library of topic vectors. You can precompute and store TSR_t for a fixed set of topics (like "security", "hashing", etc). Then, at query time, if the user asks for "security", you can immediately retrieve scores from TSR_security without recomputing from scratch. This is more scalable than computing a brand new Personalized PageRank for every query.

---

## 4. Direct Comparison

Below are the main conceptual and operational differences.

1. Teleportation behavior
   - Normal PageRank:
     Teleport goes to any node uniformly.
     Teleport vector is uniform: u(i) = 1 / N for all i.
   - Personalized PageRank:
     Teleport goes to a user defined or seed defined set.
     Teleport vector is p(i), which can be very peaked.
   - Topic-Sensitive PageRank:
     Teleport goes to a topic defined set.
     Teleport vector is p_t(i), which is peaked around nodes relevant to topic t.

2. What is being ranked
   - Normal PageRank:
     Ranks global importance across the entire graph.
     Question answered: "Who is important overall."
   - Personalized PageRank:
     Ranks importance relative to a chosen set of starting points.
     Question answered: "Who is important to me or to these seed nodes."
   - Topic-Sensitive PageRank:
     Ranks importance within a conceptual area or topic.
     Question answered: "Who is important in topic t."

3. Interpretability
   - Normal PageRank:
     Easy to interpret globally.
     High score means "this node is central in the full network."
   - Personalized PageRank:
     Interpretable if you know the seed preference.
     You must say "high score, given that we cared about nodes X, Y, Z."
   - Topic-Sensitive PageRank:
     Interpretable with respect to clearly defined topics.
     You can say "high score in security topic," which is meaningful in academic review, survey writing, or domain scouting.

4. Reusability
   - Normal PageRank:
     Single computation. One vector.
   - Personalized PageRank:
     Potentially different for each user or query. Many vectors.
     High cost if you need to serve many users.
   - Topic-Sensitive PageRank:
     One vector per topic. Topics can be fixed in advance.
     Good balance between flexibility and cost.

5. Failure modes
   - Normal PageRank:
     Can over-rank nodes that are globally popular but irrelevant to a specific query or topic.
   - Personalized PageRank:
     Can become too narrow if the personalization vector is extremely concentrated on only a few nodes. The output can become biased or echo-chamber like.
   - Topic-Sensitive PageRank:
     Depends on the quality of how you define "topic relevant". If you only match titles by keyword, you may miss relevant nodes, or you may include false positives (for example, a paper that uses the word "security" casually but is not really a security paper).

---

## 5. Summary

All three algorithms share the same structural backbone: a random walk with restarts. The general steady state equation is:

Score = d * M * Score + (1 - d) * TeleportVector

The only thing that changes between the three methods is the TeleportVector.

1. For Normal PageRank:
   TeleportVector is uniform over all nodes.

2. For Personalized PageRank:
   TeleportVector is defined by a user chosen or seed chosen preference vector.

3. For Topic-Sensitive PageRank:
   TeleportVector is defined by a topic specific vector that concentrates probability mass only on nodes relevant to that topic.

As a result:
- Normal PageRank measures global authority.
- Personalized PageRank measures authority relative to a chosen interest set.
- Topic-Sensitive PageRank measures authority within a well defined topic area.

In the assignment setting, this is exactly why Topic-Sensitive PageRank is useful. The graph you built from papers between 2010 and 2015 with at least 60 citations is still large and diverse. Normal PageRank will give you "top papers overall". But the question you actually need to answer is "what are the most authoritative papers in security, hashing, streaming, timeseries, and search". That is a topic focused question, and Topic-Sensitive PageRank is designed to answer it.
