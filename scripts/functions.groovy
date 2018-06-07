def connectToCluster(){
	graph = JanusGraphFactory.open("conf/gremlin-server/testing-janusgraph-hbase.properties")
	return graph.traversal().withComputer(SparkGraphComputer)
}
