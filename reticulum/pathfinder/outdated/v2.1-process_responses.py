import json
import argparse
import sys

pathfinder_responses = []
path_traced = []

def process_responses(json_filepath, second_node_hexhash, target):

    with open("pathfinder.json", 'r') as f:
        for line in f:
            pathfinder_responses.append(json.loads(line))

    return loop_through_responses(second_node_hexhash, target)


def loop_through_responses(node_hexhash, target_hexhash):
    for r in pathfinder_responses:
        if r["node_transport_hexhash"] == node_hexhash:
            path_traced.append(r["node_id"])
            if r["next_hop_hexhash"] != target_hexhash:
                return loop_through_responses(r["next_hop_hexhash"])
            else:
                return path_traced.append(target_hexhash)
        


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Packet tracer v2")

        # json file, start node, target
        parser.add_argument("-s", "--start", action="store_true", default=False, help="Start node")
        parser.add_argument("-t", "--transport", action="store_true", default=False, help="Transport/intermediate node")
        parser.add_argument("-e", "--end", action="store_true", default=False, help="End node")
        parser.add_argument("-c", "--config", action="store", default=None, help="path to alternative Reticulum config directory",type=str)
        parser.add_argument("-i", "--identities", action="store", default=None, help="path to transport/intermediate node identities", type=str)
        parser.add_argument("-d", "--destination", action="store", default=None, help="Hexhash of end node", type=str)
        
        args = parser.parse_args()
  
        process_responses(args.filepath, args.nh)
    except KeyboardInterrupt:
       print("")
       sys.exit(0)