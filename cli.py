from node import *
import re
from argparse import ArgumentParser
import ipaddress

all_commands = {
    "node <node_id>" : "Selects the node with id <node_id>. The selection of the node is saved until a new execution of this command has occured.",
    "t <recipient_address> <amount>": "Sends <amount> NBC coins from the wallet of the selected node, to the wallet with <recipient_address> address.",
    "nt <recipient_node_id> <amount>": "Sends <amount> NBC coins from the wallet of the selected node, to the wallet of the owner with <recipient_node_id> id.",
    "balance": "Shows the balance of the selected node's wallet.",
    "view": "Shows all the transactions of the latest validated block, of the whole noobcash blockchain.",
    "exit": "Exits Noobcash client.",
    "help": "Explains the aforementioned commands."
}

def show_all_commands():
    for command, explanation in all_commands.items():
        print("\n" + command + ": " + explanation)

    print("\n")

def check_ipv4_address(ip_address):
    # ip_pattern = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|\d)\d)\.?\b){4}$'
    # return re.match(ip_pattern, ip_address)
    try:
        ipaddress.ip_address(ip_address)
    except:
        return False

    return True

def check_status_code(response_status_code, expected_status_code = 200):
    return response_status_code == expected_status_code


parser = ArgumentParser()
parser.add_argument('--bootstrap_ip', default='192.168.0.3', type=str)
parser.add_argument('--bootstrap_port', default='5000', type=str)
args = parser.parse_args()

bootstrap_ip_address = args.bootstrap_ip
bootstrap_port = args.bootstrap_port
bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port


def set_node_url(cur_node_details):
    cur_node_ip = cur_node_details['node_details'][1]
    cur_node_port = cur_node_details['node_details'][2]
    cur_node_url = 'http://' + cur_node_ip + ":" + cur_node_port

    return cur_node_url


def view_transactions(cur_node_url):
    response = requests.get(cur_node_url + '/last-block-transactions')
    response = response.json()
    transactions = response['transactions']
    print(transactions)
    print("TRANSACTIONS INSIDE THE LATEST VALIDATED BLOCK")
    counter = 1

    # return OrderedDict({'transaction_id': self.transaction_id,
    #                     'sender_address': self.sender_address,
    #                     'recipient_address': self.receiver_address,
    #                     'transaction_inputs': self.transaction_inputs,
    #                     'transaction_outputs': self.transaction_output,
    #                     'value': self.amount,
    #                     'signature': self.signature})
    for tr in transactions:
        print(type(tr))
        tr = json.loads(tr)
        # tr_dict = tr.items()
        # print(tr)
        # print(type(tr))
        # print(tr_dict)
        #print('------------------------- Transaction id {}-------------------------------\n'.format(tr["transaction_id"]))
        print("Sender Address:", tr['sender_address'])
        print("Recipient Address:",tr['recipient_address'])
        print("Transaction Inputs:",tr['transaction_inputs'])
        print("Transaction Outputs:",tr['transaction_outputs'])
        print("Amount:",tr['value'])
        print("Signature:",tr['signature'])
        print("\n")

        # print(tr.items())
        # print()
        counter+=1

print("Welcome to Noobcash client!")
response = requests.get(bootstrap_node_url + '/get-network')
if not check_status_code(response.status_code, 200):
    exit("Could not retrieve network from bootstrap node!")

network = response.json()['network']

print("Network Details (Wallet public key, IP Address, Port)")
for key, values in network.items():
    print("\nNode " + key + ": ",  values)


cur_node_id = None
while(1):
    command = input("Type the command \"help\", to see the provided functionalities. Otherwise, proceed with the execution of a command:")
    command = command.split()
    if(command[0]=="help" and len(command) == 1):
        show_all_commands()

    elif command[0] == "node" and  len(command) == 2:
        if not command[1].isdigit():
            print("Node id must be a number!")
            continue

        node_id = {"node_id":command[1]}
        response = requests.get(bootstrap_node_url + '/specific-node', json = node_id)

        if not check_status_code(response.status_code, 200):
            print("Node with id", command[1], "does not exist in the network! Try a different number.")
            continue

        cur_node_details = response.json()
        cur_node_id = command[1]
        cur_node_url = set_node_url(cur_node_details)
        print("Node with id", command[1], "is selected.")


    elif command[0] == "balance" and len(command) == 1:
        if cur_node_id is None:
            print("No node is selected. You must first execute the command node <node_id>, to select a node.")
            continue


        response = requests.get(cur_node_url + '/balance')
        if not check_status_code(response.status_code, 200):
            print("Node with id", cur_node_id, "does not exist in the network! Try a different number.")
            continue

        response = response.json()
        print("The balance of node with id", cur_node_id, "is:", response['balance'])


    elif command[0] == "t" and len(command) == 3:
        if cur_node_id is None:
            print("No node is selected. You must first execute the command node <node_id>, to select a node.")
            continue

        # if not check_ipv4_address(command[1]):
        #     print("Invalid IPv4 address!")
        #     continue

        if command[1] == cur_node_id:
            print("A node cannot send money to itself. Transaction aborted.")
            continue


        if not (command[2].isdigit() or int(command[2])>0.0):
            print("Amount must be a positive number!")
            continue

        response = requests.get(cur_node_url + '/balance')
        if not check_status_code(response.status_code, 200):
            print("Error with executing current command! Try again.")
            continue

        response = response.json()
        balance = response['balance']

        if balance < int(command[2]):
            print("Not enough NBC for this transaction!")
            continue



        wallet_public_key = command[1]
        NBC = command[2]
        details = {"wallet_public_key": wallet_public_key, "NBC": NBC}
        response = requests.get(bootstrap_node_url + '/find-wallet-public-key', json = details) #to eixa me cur_node_url
        if not check_status_code(response.status_code, 200):
            print("Wallet with public key", wallet_public_key, "does not exist in the network! Try a different wallet public key.")
            continue
        response = response.json()

        response = requests.post(cur_node_url + '/create-client-transaction', json = details)

        if not check_status_code(response.status_code, 201):
            print("Transaction was not successful!")
            continue

        print("Successful transaction.")

        #GENIKA NA DOUME AN THA DEXOMASTE KAI FLOATS WS AMOUNT STA TRANSACTIONS, OXI MONO EDW PANTOY STO PROGRAMMA GIATI TWRA SKAEI ME FLOATS
        #proeraitiko apla gia kalh praktikh isws prosthesoume merikes getter/setters functions.

    elif command[0] == "nt" and len(command) == 3:
        if cur_node_id is None:
            print("No node is selected. You must first execute the command node <node_id>, to select a node.")
            continue

        if command[1] == cur_node_id:
            print("A node cannot send money to itself. Transaction aborted.")
            continue


        if not (command[2].isdigit() or int(command[2])>0.0):
            print("Amount must be a positive number!")
            continue

        response = requests.get(cur_node_url + '/balance')
        if not check_status_code(response.status_code, 200):
            print("Error with executing current command! Try again.")
            continue

        response = response.json()
        balance = response['balance']

        if balance < int(command[2]):
            print("Not enough NBC for this transaction!")
            continue


        recipient_node_id = command[1]
        NBC = command[2]
        details = {"node_id": str(recipient_node_id)}
        response = requests.get(bootstrap_node_url + '/find-id', json = details)
        if not check_status_code(response.status_code, 200):
            print("Node with id", recipient_node_id, "does not exist in the network! Try a different wallet public key.")
            continue
        response = response.json()

        details = {"wallet_public_key": response['wallet_public_key'], "NBC": NBC}
        response = requests.post(cur_node_url + '/create-client-transaction', json = details)

        if not check_status_code(response.status_code, 201):
            print("Transaction was not successful!")
            continue

        print("Successful transaction.")


    elif command[0] == "view" and len(command) == 1:

        view_transactions(bootstrap_node_url)


    elif command[0] == "chainlength" and len(command) == 1:

        if cur_node_id is None:
            print("No node is selected. You must first execute the command node <node_id>, to select a node.")
            continue

        response = requests.get(cur_node_url + '/blockchain-length')
        if not check_status_code(response.status_code, 200):
            print("Problem with retrieving blockchain length of current node!")
            continue
        response = response.json()
        print("Blockchain length of current node:", response['length'])


    elif command[0] == "exit" and len(command) == 1:
        exit("Noobcash client Ending...")

    else:
        print("Wrong command! Try again.")

    time.sleep(0.1)



