import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_transaction(self, sender, recipient, amount):

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index']+1

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            # TODO
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': previous_hash or self.hash(self.last_block)
        }

        # Reset the current list of transactions
        self.current_transactions = []

        # Append the block  to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        string_block = json.dumps(block, sort_keys=True)

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        raw_hash = hashlib.sha256(string_block.encode())
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        hex_hash = raw_hash.hexdigest()
        # We must make sure that the Dictionary is Ordered,

        # or we'll have inconsistent hashes
        return hex_hash
        # TODO: Create the block_string

        # TODO: Hash this string using sha256

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format

    @property
    def last_block(self):
        return self.chain[-1]

    # def proof_of_work(self, block):
    #     """
    #     Simple Proof of Work Algorithm
    #     Stringify the block and look for a proof.
    #     Loop through possibilities, checking each one against `valid_proof`
    #     in an effort to find a number that is a valid proof
    #     :return: A valid proof for the provided block
    #     """
    #     # TODO
    #     block_string = json.dumps(block, sort_keys=True)

    #     proof = 0
    #     while self.valid_proof(block_string, proof) is False:
    #         proof += 1
    #     return proof        # return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string + proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """

        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:6] == '000000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET', 'POST'])
def mine():

    # Run the proof of work algorithm to get the next proof

    # Forge the new Block by adding it to the chain with the proof
    data = request.get_json()
    print(data)
    if not data or not data['proof'] or not data['id']:
        response_code = 400
        response = {
            'message': 'Error: no proof or id provided.'
        }

    else:
        proof = data['proof']
        previous_block = blockchain.last_block
        previous_block_string = json.dumps(previous_block, sort_keys=True)

        if blockchain.valid_proof(previous_block_string, proof):
            blockchain.new_transaction('0', data['id'], 1)
            previous_hash = blockchain.hash(blockchain.last_block)
            block = blockchain.new_block(proof, previous_hash)
            response_code = 200
            response = {
                'new_block': block,
                'message': 'New Block Forged'
            }
        else:
            response_code = 400
            response = {
                'message': 'Unable to verify proof.'
            }
    return jsonify(response), response_code


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'message': 'hello',
        # TODO: Return the chain and its current length
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block
    }

    return jsonify(response), 200


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        response = {
            'message': 'missing values.'
        }
        return jsonify(response), 400

    index = blockchain.new_transaction(
        values['sender'], values['recipient'], values['amount'])
    response = {
        'message': f'Transaction will be added to block {index}'
    }

    return jsonify(response), 201


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
