def program_setup(configpath):
    reticulum = RNS.Reticulum(configpath)
    identity = RNS.Identity()
    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "minimalsample"
    )
    destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
    announceLoop(destination)

- configpath is the file path to RNS config file. From there, it will know what interfaces to use. Edit it at ~/.reticulum/config


RNS.log
- print stuff on console

RNS.Destination
- .set_proof_strategy(RNS.Destination.PROVE_ALL): Sets the ACK on. 

RNS.Link
- RNS.Link(<server_destination>): Creates a link
- .set_link_closed_callback(callback)
- .get_channel().send(<message>): Send a message
- .teardown: Close the link
- .request(...)

RNS.MessageBase
- Parent class for any data type you want to send.
- Subclasses must have a MSGTYPE assigned, where MSGTYPE >= 0xf000

RNS.Channel.Channel
- .MDU(): Maximum data unit (smaller than RNS.Link.get_mdu() to account for message headers)
- .register_message_type(Message): In order to be able to send the message type over the link
- .add_message_handler(): Add multiple handlers as callbacks. Hadndler will return True if message has been handled and processing of message stops. Else, pass to next handler.
- .is_ready_to_send(): Check if channel is ready to send

message.data
- to read a message


