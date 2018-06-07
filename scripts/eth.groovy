def addTransaction(graph, address_from_id, transaction_id, block_n, transaction_input, transactionValue, address_to_id) {
	g = graph.traversal()

	r = g.V().has('address', 'id_0x', address_from_id).limit(1).hasNext()
	if ( r ){
		address_from = g.V().has('address', 'id_0x', address_from_id).next()
	} else {
		address_from = graph.addVertex(label, 'address', 'id_0x', address_from_id)
	}

	r = g.V().has('address', 'id_0x', address_to_id).limit(1).hasNext()
	if ( r ){
		address_to = g.V().has('address', 'id_0x', address_to_id).next()
	} else {
		address_to = graph.addVertex(label, 'address', 'id_0x', address_to_id)
	}

	transaction = graph.addVertex(label, 'transaction', 'id_0x', transaction_id, 'block_n', block_n, 'transaction_input', transaction_input)
	address_from.addEdge('transfer', transaction, 'direction', 'from', 'value', transactionValue, 'currency', 'ethereum')
	transaction.addEdge('transfer', address_to, 'direction', 'to', 'value', transactionValue, 'currency', 'ethereum')

	g.tx().commit()
	graph.tx().commit()
}

def addLoopbackTransaction(graph, address_from_id, transaction_id, block_n, transaction_input, transactionValue) {
	g = graph.traversal()

	r = g.V().has('address', 'id_0x', address_from_id).limit(1).hasNext()
	if ( r ){
		address_from = g.V().has('address', 'id_0x', address_from_id).limit(1).next()
	} else {
		address_from = graph.addVertex(label, 'address', 'id_0x', address_from_id)
	}
	transaction = graph.addVertex(label, 'transaction', 'id_0x', transaction_id, 'block_n', block_n, 'transaction_input', transaction_input)
	address_from.addEdge('transfer', transaction, 'direction', 'from', 'value', transactionValue, 'currency', 'ethereum')
	transaction.addEdge('transfer', address_from, 'direction', 'to', 'value', transactionValue, 'currency', 'ethereum')

	g.tx().commit()
	graph.tx().commit()
}

def addContract(graph, address_from_id, transaction_id, block_n, transaction_input, contract_id, contractName) {
	g = graph.traversal()

	r = g.V().has('address', 'id_0x', address_from_id).limit(1).hasNext()
	if ( r ){
		address_from = g.V().has('address', 'id_0x', address_from_id).limit(1).next()
	} else {
		address_from = graph.addVertex(label, 'address', 'id_0x', address_from_id)
	}

	r = g.V().has('contract', 'id_0x', contract_id).limit(1).hasNext()
	if ( r ){
		contract = g.V().has('contract', 'id_0x', contract_id).limit(1).next()
	} else {
		contract = graph.addVertex(label, 'contract', 'id_0x', contract_id, 'name', contractName)
		// TODO
		// .property('tipe', 'eth_ERC20')
	}

	transaction = graph.addVertex(label, 'transaction', 'id_0x', transaction_id, 'block_n', block_n, 'transaction_input', transaction_input)
	address_from.addEdge('action', transaction, 'direction', 'from')
	transaction.addEdge('function', contract, 'direction', 'to', 'name', 'contract_creation')

	g.tx().commit()
	graph.tx().commit()
}

def addTokenTransfer(graph, address_from_id, transaction_id, block_n, transaction_input, contract_id, contractName, token_id, transactionValue) {
	g = graph.traversal()

	r = g.V().has('address', 'id_0x', address_from_id).limit(1).hasNext()
	if ( r ){
		address_from = g.V().has('address', 'id_0x', address_from_id).limit(1).next()
	} else {
		address_from = graph.addVertex(label, 'address', 'id_0x', address_from_id)
	}

	r = g.V().has('contract', 'id_0x', contract_id).limit(1).hasNext()
	if ( r ){
		contract = g.V().has('contract', 'id_0x', contract_id).limit(1).next()
	} else {
		contract = graph.addVertex(label, 'contract', 'id_0x', contract_id, 'name', contractName, 'tipe', 'eth_ERC20')
	}

	r = g.V().has('token', 'id_0x', token_id).limit(1).hasNext()
	if ( r ){
		token = g.V().has('token', 'id_0x', token_id).limit(1).next()
	} else {
		token = graph.addVertex(label, 'token', 'id_0x', token_id, 'tipe', 'eth_ERC20')
	}
	transaction = graph.addVertex(label, 'transaction', 'id_0x', transaction_id, 'block_n', block_n, 'transaction_input', transaction_input)
	address_from.addEdge('transfer', transaction, 'direction', 'from', 'value', transactionValue)
	transaction.addEdge('function', contract, 'direction', 'to', 'name', 'transfer')
	transaction.addEdge('transfer', token, 'direction', 'to', 'value', transactionValue, 'direction', 'to')

	g.tx().commit()
	graph.tx().commit()
}
