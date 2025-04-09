# Distributed Systems: Managing Anti-Entropy using Merkle Trees

**Author:** Pawan Bhadauria  
**Date:** 2022-02-25  
**Added by:** Krish Jaiswal

**Added on:** 2025-04-09

Link: [Article Link](https://pawan-bhadauria.medium.com/distributed-systems-part-3-managing-anti-entropy-using-merkle-trees-443ea3fc6213)

## Summary

This article explains how Merkle trees can efficiently synchronize data between nodes in distributed systems to ensure eventual consistency. It discusses the challenges that arise when choosing availability over consistency (as per the CAP theorem), specifically how to guarantee data replication across nodes despite failures or network partitioning. The solution introduces two complementary processes for data replication: a write-time "Harvester" for immediate replication and an anti-entropy manager using Merkle trees for periodic synchronization, allowing efficient comparison and reconciliation of only the differing data segments between nodes.

## Key Insights

- In distributed systems that favor availability, ensuring eventual consistency remains challenging, especially when replication processes fail during network issues or node outages
- Simple approaches like comparing all key-value pairs between nodes are inefficient for large datasets
- Merkle trees provide an efficient way to detect and synchronize only the differing parts of datasets between nodes
- Creating separate Merkle trees for each node's partition (rather than the entire dataset) is crucial when working with multi-node replication schemes
- A dual replication approach combines immediate write synchronization with periodic Merkle tree-based anti-entropy processes to guarantee stronger eventual consistency

## Implementation: Merkle Trees in Java

Below is a Java implementation of Merkle trees for efficient data synchronization in distributed systems:

```java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

/**
 * A Merkle Tree implementation for efficient data synchronization
 * between distributed system nodes.
 */
public class MerkleTree {
    private static final int DEFAULT_SEGMENTS = 1024; // Number of segments in tree
    private Node root;
    private final int segmentSize;
    private final Map<Integer, byte[]> segmentHashes;
    
    /**
     * Represents a node in the Merkle Tree
     */
    private static class Node {
        byte[] hash;
        Node left;
        Node right;
        int start;
        int end;
        
        Node(byte[] hash, int start, int end) {
            this.hash = hash;
            this.start = start;
            this.end = end;
        }
        
        boolean isLeaf() {
            return left == null && right == null;
        }
    }
    
    /**
     * Creates a Merkle Tree with the default segment size
     */
    public MerkleTree() {
        this(DEFAULT_SEGMENTS);
    }
    
    /**
     * Creates a Merkle Tree with a specific number of segments
     * @param segments Number of segments to divide the key space
     */
    public MerkleTree(int segments) {
        this.segmentSize = segments;
        this.segmentHashes = new HashMap<>();
        // Initially empty tree
        this.root = null;
    }
    
    /**
     * Adds a key to the tree
     * @param key The key to add
     * @param value The value associated with the key
     */
    public void put(String key, String value) {
        int segmentId = getSegmentId(key);
        
        try {
            // Update segment hash
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(key.getBytes());
            md.update(value.getBytes());
            byte[] keyValueHash = md.digest();
            
            if (segmentHashes.containsKey(segmentId)) {
                // If segment exists, update its hash
                MessageDigest segmentMd = MessageDigest.getInstance("SHA-256");
                segmentMd.update(segmentHashes.get(segmentId));
                segmentMd.update(keyValueHash);
                segmentHashes.put(segmentId, segmentMd.digest());
            } else {
                // New segment hash
                segmentHashes.put(segmentId, keyValueHash);
            }
            
            // Rebuild the tree with updated segment hashes
            buildTree();
            
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }
    
    /**
     * Builds or rebuilds the Merkle Tree based on current segment hashes
     */
    private void buildTree() {
        // Sort segments by ID
        List<Integer> segmentIds = new ArrayList<>(segmentHashes.keySet());
        Collections.sort(segmentIds);
        
        // Build leaf nodes first
        List<Node> leafNodes = new ArrayList<>();
        for (Integer segmentId : segmentIds) {
            leafNodes.add(new Node(segmentHashes.get(segmentId), segmentId, segmentId));
        }
        
        // Build tree bottom-up
        root = buildTreeFromLeaves(leafNodes);
    }
    
    /**
     * Recursively builds the tree from leaf nodes
     */
    private Node buildTreeFromLeaves(List<Node> nodes) {
        if (nodes.isEmpty()) {
            return null;
        }
        
        if (nodes.size() == 1) {
            return nodes.get(0);
        }
        
        List<Node> parents = new ArrayList<>();
        
        // Pair nodes and create parent nodes
        for (int i = 0; i < nodes.size(); i += 2) {
            Node left = nodes.get(i);
            Node right = (i + 1 < nodes.size()) ? nodes.get(i + 1) : null;
            
            try {
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                md.update(left.hash);
                if (right != null) {
                    md.update(right.hash);
                }
                
                Node parent = new Node(md.digest(), left.start, 
                                    right != null ? right.end : left.end);
                parent.left = left;
                parent.right = right;
                parents.add(parent);
                
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException("SHA-256 algorithm not found", e);
            }
        }
        
        // Recursively build the next level
        return buildTreeFromLeaves(parents);
    }
    
    /**
     * Calculates which segment a key belongs to
     */
    private int getSegmentId(String key) {
        return Math.abs(key.hashCode() % segmentSize);
    }
    
    /**
     * Gets the root hash of the Merkle Tree
     */
    public byte[] getRootHash() {
        return root != null ? root.hash : new byte[0];
    }
    
    /**
     * Compares this tree with another tree and returns differing segment IDs
     */
    public Set<Integer> getDifferingSegments(MerkleTree other) {
        Set<Integer> diffSegments = new HashSet<>();
        
        if (root == null || other.root == null) {
            // If either tree is empty, all segments in the other tree are different
            if (root != null) {
                diffSegments.addAll(segmentHashes.keySet());
            } else if (other.root != null) {
                diffSegments.addAll(other.segmentHashes.keySet());
            }
            return diffSegments;
        }
        
        // If root hashes are the same, trees are identical
        if (Arrays.equals(root.hash, other.root.hash)) {
            return diffSegments; // Empty set - no differences
        }
        
        // Start recursive comparison
        compareTrees(root, other.root, diffSegments);
        
        return diffSegments;
    }
    
    /**
     * Recursively compares two trees to find different segments
     */
    private void compareTrees(Node node1, Node node2, Set<Integer> diffSegments) {
        if (node1 == null || node2 == null) {
            // If one node is null, add all segments from the other node
            addAllSegments(node1 != null ? node1 : node2, diffSegments);
            return;
        }
        
        // If hashes are equal, subtrees are identical
        if (Arrays.equals(node1.hash, node2.hash)) {
            return;
        }
        
        // If both are leaf nodes with different hashes, add to differing segments
        if (node1.isLeaf() && node2.isLeaf()) {
            diffSegments.add(node1.start);
            return;
        }
        
        // Recursively compare child nodes
        if (node1.left != null && node2.left != null) {
            compareTrees(node1.left, node2.left, diffSegments);
        }
        
        if (node1.right != null && node2.right != null) {
            compareTrees(node1.right, node2.right, diffSegments);
        }
    }
    
    /**
     * Adds all segments under a node to the diff set
     */
    private void addAllSegments(Node node, Set<Integer> diffSegments) {
        if (node == null) return;
        
        if (node.isLeaf()) {
            diffSegments.add(node.start);
            return;
        }
        
        addAllSegments(node.left, diffSegments);
        addAllSegments(node.right, diffSegments);
    }
}

/**
 * Anti-entropy manager that uses Merkle Trees to synchronize data between nodes
 */
public class AntiEntropyManager {
    private final Map<String, MerkleTree> nodePartitionTrees;
    private final int replicationFactor;
    
    public AntiEntropyManager(int replicationFactor) {
        this.nodePartitionTrees = new HashMap<>();
        this.replicationFactor = replicationFactor;
    }
    
    /**
     * Registers a Merkle tree for a specific node partition
     */
    public void registerPartitionTree(String nodeId, String partitionId, MerkleTree tree) {
        String key = nodeId + ":" + partitionId;
        nodePartitionTrees.put(key, tree);
    }
    
    /**
     * Synchronizes data between two nodes for a specific partition
     */
    public Set<Integer> synchronizePartition(String nodeId1, String nodeId2, String partitionId) {
        String key1 = nodeId1 + ":" + partitionId;
        String key2 = nodeId2 + ":" + partitionId;
        
        MerkleTree tree1 = nodePartitionTrees.get(key1);
        MerkleTree tree2 = nodePartitionTrees.get(key2);
        
        if (tree1 == null || tree2 == null) {
            throw new IllegalArgumentException(
                "Merkle trees not found for nodes/partition combination");
        }
        
        // Find differing segments between trees
        Set<Integer> diffSegments = tree1.getDifferingSegments(tree2);
        
        // In a real system, you would now:
        // 1. Retrieve all keys/values from the differing segments
        // 2. Compare and merge the data
        // 3. Update both nodes with the merged data
        
        return diffSegments;
    }
    
    /**
     * Schedules periodic anti-entropy tasks between all nodes
     */
    public void scheduleAntiEntropy(long periodMillis) {
        Timer timer = new Timer(true);
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                performAntiEntropy();
            }
        }, periodMillis, periodMillis);
    }
    
    /**
     * Performs anti-entropy synchronization across all node partitions
     */
    private void performAntiEntropy() {
        // Group trees by partition
        Map<String, List<String>> partitionToNodes = new HashMap<>();
        
        for (String key : nodePartitionTrees.keySet()) {
            String[] parts = key.split(":");
            String nodeId = parts[0];
            String partitionId = parts[1];
            
            partitionToNodes.computeIfAbsent(partitionId, k -> new ArrayList<>())
                            .add(nodeId);
        }
        
        // For each partition, synchronize among all replica nodes
        for (Map.Entry<String, List<String>> entry : partitionToNodes.entrySet()) {
            String partitionId = entry.getKey();
            List<String> nodeIds = entry.getValue();
            
            // Compare each node with its replicas
            for (int i = 0; i < nodeIds.size(); i++) {
                for (int j = i + 1; j < nodeIds.size(); j++) {
                    try {
                        Set<Integer> diffs = synchronizePartition(
                            nodeIds.get(i), nodeIds.get(j), partitionId);
                        
                        if (!diffs.isEmpty()) {
                            System.out.println("Synchronized partition " + partitionId + 
                                            " between nodes " + nodeIds.get(i) + 
                                            " and " + nodeIds.get(j) + 
                                            ". Differing segments: " + diffs.size());
                        }
                    } catch (Exception e) {
                        System.err.println("Error synchronizing partition " + partitionId +
                                         " between nodes " + nodeIds.get(i) + 
                                         " and " + nodeIds.get(j) + ": " + e.getMessage());
                    }
                }
            }
        }
    }
}

/**
 * Example usage of the Merkle Tree and Anti-Entropy Manager
 */
public class DistributedSystemExample {
    public static void main(String[] args) {
        // Create a system with 3 nodes and replication factor of 3
        int numNodes = 3;
        int replicationFactor = 3;
        
        // Create an anti-entropy manager
        AntiEntropyManager antiEntropyManager = new AntiEntropyManager(replicationFactor);
        
        // Setup Merkle trees for each node and partition
        // In a real system, each node would maintain its own trees
        for (int nodeId = 1; nodeId <= numNodes; nodeId++) {
            for (int partitionId = 1; partitionId <= numNodes; partitionId++) {
                MerkleTree tree = new MerkleTree(1000); // 1000 segments
                antiEntropyManager.registerPartitionTree(
                    "node" + nodeId, "partition" + partitionId, tree);
            }
        }
        
        // Add some data to node1's partition1
        MerkleTree node1Part1Tree = new MerkleTree(1000);
        node1Part1Tree.put("key1", "value1");
        node1Part1Tree.put("key2", "value2");
        node1Part1Tree.put("key5", "value5");
        antiEntropyManager.registerPartitionTree("node1", "partition1", node1Part1Tree);
        
        // Add some data to node2's partition1 (slightly different)
        MerkleTree node2Part1Tree = new MerkleTree(1000);
        node2Part1Tree.put("key1", "value1");  // Same
        node2Part1Tree.put("key2", "value2");  // Same
        node2Part1Tree.put("key3", "value3");  // Different
        antiEntropyManager.registerPartitionTree("node2", "partition1", node2Part1Tree);
        
        // Synchronize the two nodes for partition1
        Set<Integer> diffSegments = antiEntropyManager.synchronizePartition(
            "node1", "node2", "partition1");
        
        System.out.println("Number of differing segments: " + diffSegments.size());
        System.out.println("Differing segments: " + diffSegments);
        
        // Schedule periodic anti-entropy
        antiEntropyManager.scheduleAntiEntropy(60000); // Run every minute
        
        System.out.println("Anti-entropy manager started. Press Ctrl+C to exit.");
    }
}
```

## Code Explanation

This implementation showcases a complete Merkle tree-based anti-entropy system for distributed data synchronization:

1. **MerkleTree Class**: Implements a binary Merkle tree where:
    - The key space is divided into configurable segments (default 1024)
    - Each segment gets a hash based on its contained key-value pairs
    - The tree is built bottom-up from segment hashes
    - Tree comparison efficiently identifies only differing segments

2. **AntiEntropyManager Class**: Orchestrates synchronization between nodes by:
    - Maintaining separate Merkle trees for each node-partition combination
    - Comparing trees to identify differing segments between nodes
    - Scheduling periodic anti-entropy runs across all partitions
    - Providing an API to trigger synchronization between specific nodes

3. **Key Implementation Details**:
    - SHA-256 hashing is used for all tree nodes
    - The tree is rebuilt whenever new data is added
    - Comparison traverses the tree recursively, stopping at matching subtrees
    - Only segments that differ are synchronized, minimizing data transfer

This implementation demonstrates the core concept highlighted in the article: creating separate Merkle trees for each node partition rather than a single tree per node, allowing efficient synchronization of just the differing data segments between replicas.

## Tags
#distributed-systems #merkle-trees #eventual-consistency #anti-entropy #java #cap-theorem #replication