# Reliable Blast UDP in Python

RBUDP is a data transport tool and protocol specifically designed to move very large files over wide area high-speed networks. It is implemented based on details in this [paper](https://www.evl.uic.edu/cavern/papers/cluster2002.pdf). Below is simple view of the protocol:

<img src="https://github.com/Yilong94/rbudp-py/blob/master/rbudp_diagram.png" width="400">

## Getting Started

__On the server side:__

From terminal, in the directory of server.py, execute the following code in this format:

```
python3 server.py [ip address of server] [transmission rate of UDP socket in Mbps]
```

* Note: the transmission rate should be lower than the overall throughput rate

As an example:

```
python3 server.py 127.0.0.1 1000.0
```

__On the client side:__

From terminal, in the directory of client.py, execute the following code in this format:

```
python3 client.py [ip address of client] [port number of client UDP socket] [ip address of server] [file name to be requested]
```

As an example:

```
python3 client.py 127.0.0.1 60000 127.0.0.1 test.pdf
```

## To-Do

* Saving bytes in memory and transmission seem to be increasing with time and is slowing down RBUDP. Needs more testing to find the root cause. Possible to make it more efficient. Might be better to write to disk, instead of RAM 
